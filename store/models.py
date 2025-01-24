from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Seller(models.Model):
	name = models.CharField(max_length=255)
	email = models.EmailField(unique=True)
	password = models.CharField(max_length=255,default=0, null=True, blank=True)
	phone_number = models.CharField(max_length=15, blank=True, null=True)
	address = models.TextField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.name

class Customer(models.Model):
	user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)  #one to one relationship between user and customer 1 user = 1  customer
	name = models.CharField(max_length=200, null=True)
	num = models.IntegerField(default=0, null=True, blank=True)
	email = models.CharField(max_length=200)
	address = models.CharField(max_length=200,default=0, null=True, blank=True)
	proimg = models.ImageField(null=True, blank=True)
	last_login = models.DateTimeField(null=True,auto_now=True)

 
	@property
	def imageURL(self):
		try:
			url = self.proimg.url   #.URL returns the publicly accessible URL of the file
		except:
			url = ''
		return url

	def __str__(self):
		return self.name or self.user.username or "Unnamed Customer"
	
	def get_email_field_name(self):
		return 'email'
	
class Catagory(models.Model):
	catagory_name = models.CharField(max_length=150, null=False, blank=False)
	image = models.ImageField(null=True, blank=True)
	Description = models.TextField(max_length=500, null=False, blank=False)
	status = models.BooleanField(default=False, help_text="0-Show, 1-Hidden")
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.catagory_name

class Product(models.Model):
	seller=models.ForeignKey(Seller,on_delete=models.CASCADE,null=True)
	catagory_name = models.ForeignKey(Catagory, on_delete=models.CASCADE)
	name = models.CharField(max_length=150, null=False, blank=False)
	price = models.FloatField()
	digital = models.BooleanField(default=False, null=True, blank=True)
	image = models.ImageField(null=True, blank=True)
	description = models.TextField(null=True, blank=True)
	stock = models.IntegerField(default=0, null=True, blank=True)

	def __str__(self):
		return self.name


	#if image not available
	@property
	def imageURL(self):
		try:
			url = self.image.url   #.URL returns the publicly accessible URL of the file
		except:
			url = ''
		return url

class Order(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)   #Foreign key Customer can order many time many to one relationship 
	date_ordered = models.DateTimeField(auto_now_add=True)
	complete = models.BooleanField(default=False)
	transaction_id = models.CharField(max_length=100, null=True)

	def __str__(self):
		return str(self.id)
		
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orderitem_set.all()  # you can access all related OrderItem objects using the orderitem_set attribute
		for i in orderitems:
			if i.product.digital == False: #order item class foreign key with order item orderitem hav product product.digital
				shipping = True
		return shipping

	@property
	def get_cart_total(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.get_total for item in orderitems])  # Use property correctly
		return total

	@property
	def get_cart_items(self):
		orderitems = self.orderitem_set.all()
		total = sum([item.quantity for item in orderitems])
		return total 

class OrderItem(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	quantity = models.IntegerField(default=0, null=True, blank=True)
	date_added = models.DateTimeField(auto_now_add=True)

	@property
	def get_total(self):
		total = self.product.price * self.quantity
		return total

class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
	order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
	address = models.CharField(max_length=200, null=False)
	city = models.CharField(max_length=200, null=False)
	state = models.CharField(max_length=200, null=False)
	zipcode = models.CharField(max_length=200, null=False)
	date_added = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.address
	
	@property
	def shipping(self):
		shipping = False
		orderitems = self.orderitem_set.all()
		for i in orderitems:
			if i.product.digital == False:
				shipping = True
		return shipping

class Wishlist(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	products = models.ManyToManyField(Product, related_name='wishlists')
	
	def __str__(self):
		return f"Wishlist of {self.user.username}"
	
class Coupon(models.Model):
	code = models.CharField(max_length=50, unique=True)
	discount = models.DecimalField(max_digits=5, decimal_places=2)  # Example: 20.00 for 20%
	valid_from = models.DateTimeField()
	valid_to = models.DateTimeField()
	active = models.BooleanField(default=True)

	def __str__(self):
		return self.code


	