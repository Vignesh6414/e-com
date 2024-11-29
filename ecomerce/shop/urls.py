from django.urls import path
from . import views
urlpatterns = [
    path('',views.home,name="home"),
    path('register',views.register,name="register"),
    path('login',views.login_page,name="login"),
    path('logout',views.logout_page,name="logout"),
    path('collections',views.collections,name="collection"),
    path('collections/<str:name>',views.collectionsviews,name="collections"),
    path('collections/<str:cname>/<str:pname>',views.product_details,name="product_details"),
    path('addtocart',views.add_to_cart,name="add_to_cart"),
    path('cart',views.card_page,name="cart_page"),
    path('fav',views.fav_page,name="fav"),
    path('fav_view_page',views.fav_view_page,name="fav_view_page"),
    path('remove_fav/<int:name>',views.remove_fav,name="remove_fav"),
    path('remove_cart/<str:name>',views.remove_cart,name="remove_cart"),

]
