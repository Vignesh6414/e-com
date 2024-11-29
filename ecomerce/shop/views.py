from django.http import JsonResponse
from django.shortcuts import redirect, render
from shop.form import CustomerUserForm
from .models import *
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.csrf import csrf_exempt
from .models import Product, cart
from django.http import JsonResponse
import json


# Create your views here.
def home(request):
    Products=Product.objects.filter(trending=1)
    return render(request,"shop/index.html",{"products":Products})

def card_page(request):
    if request.user.is_authenticated:
        Cart=cart.objects.filter(user=request.user)
        return render(request,"shop/cart.html",{"cart":Cart})
    else:
        return redirect("/")


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def fav_page(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Ensure it's an AJAX request
        if request.user.is_authenticated:  # Check if the user is logged in
            try:
                # Parse JSON data from the request
                data = json.loads(request.body)
                product_id = data.get('pid')

                # Validate product existence
                product = Product.objects.get(id=product_id)

                # Check if the product is already in favorites
                if Favorite.objects.filter(user=request.user, product_id=product_id).exists():
                    return JsonResponse({'status': 'Product Already in Favorite'}, status=200)
                
                # Add product to favorites
                Favorite.objects.create(user=request.user, product=product)
                return JsonResponse({'status': 'Product Added to Favorite'}, status=200)

            except Product.DoesNotExist:
                return JsonResponse({'status': 'Product Not Found'}, status=404)
            except json.JSONDecodeError:
                return JsonResponse({'status': 'Invalid JSON Data'}, status=400)
            except Exception as e:
                return JsonResponse({'status': 'Error', 'message': str(e)}, status=500)
        else:
            return JsonResponse({'status': 'Login to Add Favorite'}, status=401)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=400)


def fav_view_page(request):
    if request.user.is_authenticated:
        fav=Favorite.objects.filter(user=request.user)
        return render(request,"shop/fav.html",{"fav":fav})
    else:
        return redirect("/")

def remove_fav(request, name):
    try:
        # Try to fetch the favorite item
        favorite_item = Favorite.objects.get(id=name, user=request.user)  # Ensure the item belongs to the current user
        favorite_item.delete()  # Delete the item
        messages.success(request, "Item removed from favorites successfully.")
    except Favorite.DoesNotExist:
        # Handle the case where the favorite item does not exist
        messages.error(request, "Item not found in your favorites.")
    
    # Redirect to the favorites view page
    return redirect("fav_view_page")


@csrf_exempt
def add_to_cart(request):
    if request.method == "POST":
        # Extract product ID and quantity
        pid = request.POST.get('pid')
        quantity = request.POST.get('quantity', 1)  # Default to 1 if not provided

        # Validate user authentication
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'You must be logged in to add items to the cart.'}, status=401)

        try:
            # Validate product existence
            product = Product.objects.get(id=pid)

            # Convert quantity to an integer and validate range
            quantity = int(quantity)
            if quantity < 1 or quantity > 10:
                return JsonResponse({'error': 'Invalid quantity. Please choose between 1 and 10.'}, status=400)

            # Add or update product in cart
            cart_item, created = cart.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'product_qty': quantity}
            )
            if not created:
                new_quantity = cart_item.product_qty + quantity
                if new_quantity > 10:
                    return JsonResponse({'error': 'Cannot add more than 10 units of this product.'}, status=400)
                cart_item.product_qty = new_quantity
                cart_item.save()

            return redirect("cart_page")    
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found.'}, status=404)
        except ValueError:
            return JsonResponse({'error': 'Invalid quantity value.'}, status=400)

    # Handle non-POST requests
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def remove_cart(request, name):
    try:
        # Try to fetch the cart item
        cartitem = cart.objects.get(id=name)
        cartitem.delete()  # Delete the item if it exists
        messages.success(request, "Item removed from the cart successfully.")
    except cart.DoesNotExist:
        # Handle the case where the item does not exist
        messages.error(request, "Item not found in the cart.")
    
    # Redirect to the cart page
    return redirect("cart_page")


def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request,"Logged out Successfully") 
    return redirect("/")

def login_page(request):
     if request.user.is_authenticated:
         return redirect("/")
     else:
        if request.method=='POST':
            name=request.POST.get('username')
            pwd=request.POST.get('password')
            user=authenticate(request,username=name,password=pwd)
            if user is not None:
                login(request,user)
                messages.success(request,"Logged in Successfully")
                return render(request,"shop/index.html")
            else:
                messages.error(request,"Invalid User Name or Password")
                return redirect("/login")
        return render(request,"shop/login.html")

def register(request):
    form= CustomerUserForm() # type: ignore
    if request.method=='POST':
        form=CustomerUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,"Registration Success you can Login Now..!")
            return redirect('/login')
    return render(request,"shop/reg.html",{'form': form})

def collections(request):
    category=Category.objects.filter(status=0)
    return render(request,"shop/collections.html",{"category":category})

def collectionsviews(request,name):
    if(Category.objects.filter(name=name,status=0)):
        products=Product.objects.filter(category__name=name)
        return render(request,"shop/products/index.html",{"products":products,"category":name})
    else:
        messages.warning(request,"No Such Category Found")
        return redirect('collections')
    

def product_details(request,cname,pname):
    if(Category.objects.filter(name=cname,status=0)):
        if(Product.objects.filter(name=pname,status=0)):
            products=Product.objects.filter(name=pname,status=0).first()
            return render(request, "shop/products/product_details.html",{"products":products})
        else:
            messages.error(request, "No Such Products Found")
            return redirect('collections')
    else:
        messages.error(request, "No Such Category Found")
        return redirect('collections')

    