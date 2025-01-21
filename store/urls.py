from django.urls import path # type: ignore
from django.conf.urls import handler404
from . import views

handler404 = 'store.views.custom_404' 


app_name='store'
#"url paths" to call these views.
urlpatterns = [
    path('',views.store, name="store"),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutPage, name='logout'),
    path('cart/',views.cart, name="cart"),
    path('checkout/',views.checkout, name="checkout"),
    
    path('update_item/',views.updateItem, name="UpdateItem"),
    path('process_order/',views.processOrder,name="process_order"),
    path('catagory/', views.catagory, name='catagory'), 
    path('catagory/<str:catagory_name>', views.collectionsview, name='collectionsview'), 
    path('register/', views.register, name='register'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/<str:action>/', views.update_wishlist, name='update_wishlist'),
    path('add_to_wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('view/<int:product_id>/', views.view, name='view'),
    path('forgot/',views.forgot, name="forgot"),
    path('resetpassword/<uidb64>/<token>/', views.resetpassword, name='resetpassword'),
]
