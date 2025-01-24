from django import forms
from .models import * 


class CouponApplyForm(forms.Form):
    code = forms.CharField(max_length=50)

class ForgotPasswordForm(forms.Form):
    email=forms.EmailField(label='Email',max_length=256,required=True)
    
    def clean(self):
        cleaned_data=super().clean()
        email=cleaned_data.get('email')
        
        def clean_email(self):
            email = self.cleaned_data['email']
            try:
                Customer.objects.get(email=email)  # Corrected from `object` to `objects`
            except Customer.DoesNotExist:
                raise forms.ValidationError('No user found with this email address.')
            return email
        
class ResetPasswordForm(forms.Form):
    new_password = forms.CharField(label='New Password', min_length=4)
    confirm_password = forms.CharField(label='Confirm Password', min_length=4)

    # def clean(self):
    #     cleaned_data = super().clean()
    #     new_password = cleaned_data.get("new_password")
    #     confirm_password = cleaned_data.get("confirm_password")

    #     if new_password and confirm_password and new_password != confirm_password:
    #         print("hi")
    #         raise forms.ValidationError("Passwords do not match.")
    
class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['name', 'email', 'phone_number', 'address']
            
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'digital', 'image', 'description', 'stock', 'catagory_name']