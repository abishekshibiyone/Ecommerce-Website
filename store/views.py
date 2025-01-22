from django.dispatch import receiver
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import now
from .forms import *
from django.http import HttpResponse, JsonResponse
import json
import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import * 
from django.contrib.auth.decorators import login_required  # Import the decorator
from .utils import cookieCart, guestOrder
from decimal import Decimal
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import  render_to_string
from django.core.mail import send_mail



#	@login_required(login_url='login')
def store(request):
	query = request.GET.get('query', '')  # Get search query for the name
	min_price = request.GET.get('min_price', None)  # Get minimum price
	max_price = request.GET.get('max_price', None)  # Get maximum price
	wish=''
	# Fetch all products
	products = Product.objects.all()

	# Apply filters
	if query:
		products = products.filter(name__icontains=query)  # Case-insensitive name search

	if min_price:
		products = products.filter(price__gte=min_price)  # Price greater than or equal to min_price

	if max_price:
		products = products.filter(price__lte=max_price)  # Price less than or equal to max_price

	# Handle cart data and user authentication
	if request.user.is_authenticated:
		try:
			# Ensure the customer exists
			customer = request.user.customer
			wish = set(Wishlist.objects.filter(user_id=customer.id).values_list('products',flat=True)) if customer else set()
			print(wish)
		except Customer.DoesNotExist:
			# Create a customer if it doesn't exist
			customer = Customer.objects.create(user=request.user)

		# Fetch cart data
		data = cartData(request)
		cartItems = data['cartItems']
	else:
		# For unauthenticated users, use session-based cart
		data = cartData(request)
		cartItems = data['cartItems']

	# Pass filtered products to the context	
	
	context = {
		'products': products,
		'cartItems': cartItems,
		'wish':wish,
		# 'customer':customer,
	}
	return render(request, 'store/store.html', context)



def cartData(request):
	"""
	Handles cart data for both authenticated and non-authenticated users.
	"""
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		# For anonymous users
		cookieData = cookieCart(request)
		items = cookieData['items']
		cartItems = cookieData['cartItems']

		# Create a placeholder order for unauthenticated users
		order = {'get_cart_total': 0, 'get_cart_items': cartItems, 'shipping': False}

	return {'items': items, 'order': order, 'cartItems': cartItems}


def cart(request):

	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)


# def checkout(request):

# 	data = cartData(request)
# 	cartItems = data['cartItems']
# 	order = data['order']
# 	items = data['items']

# 	context = {'items':items, 'order':order, 'cartItems':cartItems}
# 	return render(request, 'store/checkout.html', context)



def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity += 1
	elif action == 'remove':
		orderItem.quantity -= 1
	
	if orderItem.quantity<=product.stock:
		orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)


def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)

def loginPage(request):
	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')
  
		username=User.objects.get(email=email)
		print(username)	
		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('store:store')  # Redirect to the store page after login
		else:
			messages.error(request, 'Invalid username or password')

	return render(request, 'store/login.html')


def logoutPage(request):
	logout(request)
	return redirect('store:store') # Redirect to the login page after logout


def register(request):
	if request.method == 'POST':
		username = request.POST['username']
		email = request.POST['email']
		password1 = request.POST['password1']
		password2 = request.POST['password2']

		# Check if passwords match
		if password1 != password2:
			messages.error(request, "Passwords do not match!")
			return redirect('register')
		
		# Check if username already exists
		if User.objects.filter(username=username).exists():
			messages.error(request, "Username already taken!")
			return redirect('register')
		
		# Check if email already exists
		if User.objects.filter(email=email).exists():
			messages.error(request, "Email already in use!")
			return redirect('register')

		# Create and save the user
		user = User.objects.create_user(username=username, email=email, password=password1)
		user.save()
		messages.success(request, "Account created successfully!")
		return redirect('login')
	
	return render(request, 'store/register.html')

def forgot(request):
    form = ForgotPasswordForm()
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                print(token)
                print(uid)
                current_site = get_current_site(request)
                domain = current_site.domain
                print(domain)
                subject = "Reset Password Requested"
                message = render_to_string('store/resetpassword.html', {
                    'domain': domain,
                    'uidb64': uid,
                    'token': token,
                })
                send_mail(subject, message, 'noreply@abishek.com', [email])
                messages.success(request, 'An email has been sent with reset instructions.')
            except User.DoesNotExist:
                print("no email found")
                messages.error(request, 'No account found with that email.')
    return render(request, 'store/forgot.html', {'form': form})

def resetpassword(request, uidb64, token):
	form = ResetPasswordForm()
	if request.method == 'POST':
		#form
		print("1")
		form = ResetPasswordForm(request.POST)
		if form.is_valid():
			
			new_password = form.cleaned_data['new_password']
			print(new_password)
			try:
				uid = urlsafe_base64_decode(uidb64)
				user = User.objects.get(pk=uid)
			except(TypeError, ValueError, OverflowError, User.DoesNotExist):
				user = None

			if user is not None and default_token_generator.check_token(user, token):
				user.set_password(new_password)
				user.save()
				messages.success(request, 'Your password has been reset successfully!')
				return redirect('store:login')
			else :
				messages.error(request,'The password reset link is invalid')

	return render(request,'store/resetpasswordemail.html', {'form': form})
	


  

def create_customer(sender, instance, created, **kwargs):
	if created:
		Customer.objects.create(user=instance)


def save_customer(sender, instance, **kwargs):
	if hasattr(instance, 'customer'):
		instance.customer.save()
		
def add_to_wishlist(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	wishlist, created = Wishlist.objects.get_or_create(user=request.user)
	wishlist.products.add(product)
	return redirect('store')  # Redirect to the store page (adjust if needed)

@login_required
def remove_from_wishlist(request, product_id):
	product = get_object_or_404(Product, id=product_id)
	wishlist = Wishlist.objects.get(user=request.user)
	wishlist.products.remove(product)
	return redirect('store:wishlist')  # Redirect to the wishlist page

@login_required
def wishlist(request):
	data = cartData(request)
	cartItems = data['cartItems']
	wishlist, created = Wishlist.objects.get_or_create(user=request.user)
	context = {
		'wishlist': wishlist,
		'cartItems': cartItems
	}
	return render(request, 'store/wishlist.html', context)

@login_required
def update_wishlist(request, action):
	if request.method == 'POST':
		try:
			# Parse JSON data
			data = json.loads(request.body)
			product_id = data.get('product_id')

			if not product_id:
				return JsonResponse({'success': False, 'error': 'Product ID is required.'}, status=400)

			# Fetch the product and wishlist
			product = get_object_or_404(Product, id=product_id)
			wishlist, created = Wishlist.objects.get_or_create(user=request.user)

			# Perform add or remove action
			if action == 'add':
				wishlist.products.add(product)
			elif action == 'remove':
				wishlist.products.remove(product)
			else:
				return JsonResponse({'success': False, 'error': 'Invalid action.'}, status=400)

			return JsonResponse({'success': True})
		except json.JSONDecodeError:
			return JsonResponse({'success': False, 'error': 'Invalid JSON data.'}, status=400)
		except Exception as e:
			return JsonResponse({'success': False, 'error': str(e)}, status=500)

	return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)


def profile(request, username):
	
	
	try:
		customer = Customer.objects.get(name=username)
		orderitems = OrderItem.objects.filter(customer=customer)
		shipping_addresses = ShippingAddress.objects.filter(customer=customer)
		order = Order.objects.filter(customer=customer)
		
	except Customer.DoesNotExist:
		# Handle case where customer does not exist
		return redirect('some_error_page')  # You can redirect to an error page or a default profile page
	
	# If the request method is POST, update the profile data
	if request.method == "POST":
		customer.name = request.POST.get('name')
		customer.num = request.POST.get('num')
		customer.email = request.POST.get('email')
		customer.address = request.POST.get('address')
		if 'proimg' in request.FILES:  # Check if a new profile image is uploaded
			customer.proimg = request.FILES['proimg']
		customer.save()
		return redirect('profile', username=customer.name)  # Redirect to the updated profile page
	context={
		'customer': customer,
		'orderitems': orderitems, 
  		'shipping_addresses': shipping_addresses,
		'order':order,
	}
	# Rendering the profile page
	return render(request, 'store/profile.html', context)

def view(request, product_id):
	product = Product.objects.get(id=product_id)
	context={
		'product': product,
	}
	return render(request,'store/view.html',context)

def custom_404(request, exception):
	return render(request, 'store/404.html', status=404)


def checkout(request):
	# Retrieve cart data
	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	
	# Calculate total price using the order's get_cart_total method
	total_price = Decimal(order.get_cart_total)  # Ensure it's a Decimal
	
	# Initialize discount and coupon variables
	discount = Decimal('0.00')
	discounted_total = total_price  # Start with the total price
	payment_amount = total_price  # Default to the original total price
	message = None
	coupon_code = request.POST.get('coupon_code', None)

	# Handle coupon code if provided
	if coupon_code:
		try:
			# Validate the coupon
			coupon = Coupon.objects.get(
				code=coupon_code, valid_from__lte=now(), valid_to__gte=now(), active=True
			)
			discount = (Decimal(coupon.discount) / 100) * total_price
			discounted_total -= discount
			payment_amount = discounted_total
			message = f"Coupon applied! You saved {discount:.2f}."
		except Coupon.DoesNotExist:
			message = "Invalid or expired coupon code."
			payment_amount = total_price

	# Context for rendering the template
	context = {
		'items': items,
		'order': order,
		'cartItems': cartItems,
		'total_price': total_price,
		'discount': discount,
		'discounted_total': discounted_total,
		'payment_amount': payment_amount,  # Add payment_amount to the context
		'message': message,
	}

	return render(request, 'store/checkout.html', context)


def catagory(request):
	data = cartData(request)
	cartItems = data['cartItems']
	catagory = Catagory.objects.filter(status=0)
	return render(request,'store/catagory.html',{"catagory":catagory,'cartItems': cartItems})
 
def collectionsview(request, catagory_name):
	data = cartData(request)
	cartItems = data['cartItems']
	if Catagory.objects.filter(catagory_name=catagory_name, status=0).exists():
		products = Product.objects.filter(catagory_name__catagory_name=catagory_name)
		return render(request, 'store/index.html', {"products": products, "category": catagory_name,'cartItems': cartItems})
	else:
		messages.warning(request, "No details are available for the selected category.")
		return redirect('catagory')

def add_seller(request):
    if request.method == "POST":
        form = SellerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('success')  # Replace 'success' with your success page URL
    else:
        form = SellerForm()
    return render(request, 'add_seller.html', {'form': form})