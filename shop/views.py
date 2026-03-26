from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic import DetailView ,ListView , FormView , CreateView , DeleteView,TemplateView
from .models import Product , CartItem ,Ecurrency , TransactionHistory
from django.http import JsonResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models import Q
from django.http import HttpResponseRedirect

# Create your views here.

class home(ListView):
    model = Product
    template_name = "home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['smartphones'] = Product.objects.filter(subcategory='Smartphones')
        context['watches'] = Product.objects.filter(subcategory='watch')
        context['discount'] = Product.objects.filter(subcategory='discount')
        context['page1'] = Product.objects.filter(subcategory='page1')
        context['page2'] = Product.objects.filter(subcategory='page2')
        context['audio'] = Product.objects.filter(subcategory='Audio Accessories')[:3]
        context['Laptops'] = Product.objects.filter(subcategory='Laptops')[:3]
        context['audio_second'] = Product.objects.filter(subcategory='Audio Accessories')[3:6]
        context['Speakers'] = Product.objects.filter(subcategory='Speakers')[:3]
        context['Speakers1'] = Product.objects.filter(subcategory='Speakers')[3:6]
        context['MemoryCards'] = Product.objects.filter(subcategory='Memory Cards')[:3]
        context['MemoryCards1'] = Product.objects.filter(subcategory='Memory Cards')[3:6]
        context['audio_third'] = Product.objects.filter(subcategory='Audio Accessories')[6:9]
        return context

def SmartPhones(request):
    template_name = "SmartPhones.html"
    smartphones = Product.objects.filter(subcategory='Smartphones')
    no_items_found = False
    
    if request.method == 'POST':
        price_range = request.POST.get('price_range')
        if price_range:
            min_price, max_price = map(int, price_range.split('-'))
            smartphones = smartphones.filter(price__gte=min_price, price__lte=max_price)
    
    if not smartphones:  # If no items found
        no_items_found = True
    
    context = {'smartphones': smartphones, 'no_items_found': no_items_found}
    return render(request, template_name, context)

class Watches(ListView):
    model = Product
    template_name = "Watches.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['watches'] = Product.objects.filter(subcategory='watch')
        return context
class MemoryCards(ListView):
    model = Product
    template_name = "MemoryCards.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['MemoryCards'] = Product.objects.filter(subcategory='Memory Cards')
        return context
class monitors(ListView):
    model = Product
    template_name = "monitors.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Laptops'] = Product.objects.filter(subcategory='Laptops')
        return context
class Speakers(ListView):
    model = Product
    template_name = "Speakers.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['Speakers'] = Product.objects.filter(subcategory='Speakers')
        return context
class product_detail(DetailView):
    model = Product
    template_name = "product_detail.html"
    context_object_name = "product_data"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        related_products = Product.objects.filter(category=self.object.category).exclude(prod_id=self.object.prod_id)[:4]
        context['related_products'] = related_products
        return context


def send(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        product_name = request.POST.get('product_name')
        num = request.POST.get('num')
        product_image = request.POST.get('product_image')
        price = request.POST.get('price')

        # Assuming you have a logged-in user (login_required decorator ensures this)
        user = request.user
        # Try to get the existing cart item, or create a new one if not found
        cart_item, created = CartItem.objects.get_or_create(user=user, product_name=product_name,image=product_image,price = price)

        # If the cart item exists, update the quantity
        if not created:
            cart_item.quantity += int(num)
            cart_item.save()

        response_data = {
            'message': 'Data received and stored in the cart successfully',
            'username': username,
            'product_name': product_name,
            'num': num,
        }

        return JsonResponse(response_data)
    else:
        return JsonResponse({'error': 'Please login to view the cart'})
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("/")
            # Redirect to a success page, or whatever you need
        else:
            message = "Invalid username or password. Please try again."
            return render(request, 'login.html', {'message': message})

    return render(request, 'login.html')
    
class logout(LogoutView):
    def get(self, request, *args, **kwargs):
        # Perform any additional logic before logging out
        return render(request, "logout.html")
    

def cart_list(request):
    # Fetch cart items for the logged-in user
    cart_items = CartItem.objects.filter(user=request.user)

    total_items = cart_items.count()
    total_price_to_pay = 0
    delivery_date_str = ""
    message = "" 
    after_shipping = 0  # Initialize after_shipping with a default value
    if cart_items.exists():
        for item in cart_items:
            item.total = item.price * item.quantity
            total_price_to_pay += item.total

        delivery_date_start = datetime.now() + timedelta(days=15)
        delivery_date_end = delivery_date_start + timedelta(days=2)  # Assuming a two-day delivery window

        after_shipping = total_price_to_pay + 20

        # Format delivery date as string
        delivery_date_str = f"{delivery_date_start.strftime('%d.%m.%Y')} - {delivery_date_end.strftime('%d.%m.%Y')}"
    else:
        message = "Your cart is empty."
    context = {
        'cart_items': cart_items,
        'total_items': total_items,
        'after_shipping': after_shipping,
        'delivery_date': delivery_date_str,  # Include formatted delivery date in context
        'total_price_to_pay': total_price_to_pay,  # Include total price to pay in context
        'message': message,
        
    }
    print("Server Response:", context)
    return render(request, 'cart_list.html', context)


from django.core.serializers import serialize
def get_data(request):
    if request.method == "GET" and request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        total_items = cart_items.count()
        total_price = sum(item.price * item.quantity for item in cart_items)

        # Serialize cart items
        cart_items_serialized = serialize('json', cart_items)

        return JsonResponse({
            "total_items": total_items,
            "total_price": total_price,
            "cart_items": cart_items_serialized,
        }, safe=False)  # Set safe to False to allow serializing lists
    else:
        return JsonResponse({"error": "User not authenticated"}, status=403)

    
def delete_add_item(request):
    if request.method == "POST":
        product_name = request.POST.get("product_name")
        
        if product_name is not None:
            try:
                cart_item = CartItem.objects.get(product_name=product_name)
                cart_item.delete()
                return JsonResponse({"product_name": product_name})
            except CartItem.DoesNotExist:
                return JsonResponse({"error": f"Product with name {product_name} not found"}, status=404)
        else:
            return JsonResponse({"error": "Product name not provided"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
    
from .models import UserAddress
class checkout(ListView):
    model = CartItem
    template_name = "checkout.html"
    context_object_name = "data"

    def get_queryset(self):
        # Filter CartItem instances for the current user
        return CartItem.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for item in context["object_list"]:
            item.total = item.price * item.quantity

        total_price = sum(item.price * item.quantity for item in context["data"])
        context["totalPrice"] = total_price
        
        return context
    
    def post(self, request, *args, **kwargs):
    # Extract user address information from the form
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        address = request.POST.get('address')
        city = request.POST.get('city')
        house = request.POST.get('house')
        postalcode = request.POST.get('postalcode')
        zip_code = request.POST.get('zip')
        message_to_seller = request.POST.get('message_to_seller')

        # Create a UserAddress instance and save it to the database
        user_address = UserAddress.objects.create(
            firstname=firstname,
            lastname=lastname,
            phone=phone,
            email=email,
            address=address,
            city=city,
            house=house,
            postalcode=postalcode,
            zip=zip_code,
            message_to_seller=message_to_seller
        )

        # Additional logic if needed

        # Clear the user's cart after completing the checkout

        return redirect('checkoutview')
    
from .models import Order
class history(ListView):
    model =  Order
    context_object_name = "orders"
    template_name = "history.html"

    def get_queryset(self):
        # Filter orders for the current user
        return Order.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = self.get_queryset()
        # Summing up the prices of all items in all orders
        sub_total = sum(item.price  for item in orders)
        dates = [order.order_date for order in orders]
        user_addresses = UserAddress.objects.filter(user=self.request.user)
        total_price = sub_total + 20
        print(user_addresses)
        context['sub_total'] = sub_total
        context['total_price'] = total_price
        context['dates'] = dates
        context['user_addresses'] = user_addresses
        return context
    
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

def signup(request):
    if request.method == 'POST':
        username = request.POST['name']
        email = request.POST['email']
        password = request.POST['pass']
        re_password = request.POST['re_pass']

        if password != re_password:
            # Handle password mismatch error
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        # Check if user with the same username or email already exists
        if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
            # Handle user already exists error
            return render(request, 'signup.html', {'error': 'User already exists'})

        # Create the user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        Ecurrency.objects.create(user=user)

        # Log the user in
        user = authenticate(username=username, password=password)
        login(request, user)

        # Redirect to home page or any other page
        return redirect('home')

    return render(request, 'signup.html')

def payment(request):   
    cart_items = CartItem.objects.filter(user = request.user)
    total_price = sum(item.price * item.quantity for item in cart_items)

    return render(request, "payment.html",{"total_price": total_price})


def checkoutview(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        if payment_method == 'paypal':
            # Redirect to PayPal page
            return redirect('payment')
        elif payment_method == 'ecurrency':
            return redirect('ecurrency') 
         
    return render(request, 'payment_gateway.html')

def ecurrency(request):
    current_user = request.user
    eCurrency_obj = Ecurrency.objects.get(user=current_user)
    eCurrency = eCurrency_obj.amount
    all_saved = CartItem.objects.filter(user=request.user).all()
    total_amount = 20  # Assuming initial total amount
    
    # Calculate total amount of all items in the cart
    for individual in all_saved:
        total_amount += individual.price 

    if request.method == 'POST':
        eCurrency_str = request.POST.get("eCurrency")
        amount_str = request.POST.get("amount")
        print(eCurrency_str)
        print(amount_str)
        eCurrency = int(eCurrency_str)
        amount = total_amount
        
        print("i am up")
        if eCurrency < amount: 
            error = "You have less amount in your e-wallet. Kindly go with the alternative payment."
            return render(request, "ecurrency.html", {"eCurrency": eCurrency, "total_amount": amount, "error": error})
        else:
            print("i am down")
            # Deduct amount from eCurrency
            new_eCurrency = eCurrency - amount
            eCurrency_obj.amount = new_eCurrency
            eCurrency_obj.save()

            # Create order entries for each item in the cart
            for item in all_saved:
                # Get the Product instance associated with the item
                product_instance = Product.objects.filter(prod_name=item.product_name).first()
                if product_instance:
                    Order.objects.create(
                        user=current_user,
                        product=product_instance,  # Associate the Product instance with the Order
                        quantity=item.quantity,
                        price=item.price,
                        image=item.image
                    )

            # Add entry to TransactionHistory
            TransactionHistory.objects.create(
                user=current_user,
                amount=amount,
                transaction_type="Payment",
            )

            # Clear the cart after successful payment
            all_saved.delete()
            return redirect("success")
                # Redirect to a success page # Replace 'success-page' with your actual URL name
        
    return render(request, "ecurrency.html", {"eCurrency": eCurrency, "total_amount": total_amount, "cart_items": all_saved})

def success(request):
    # Retrieve the latest order details for the current user
    latest_order = Order.objects.filter(user=request.user).order_by('-order_date').first()

    context = {'latest_order': latest_order}
    return render(request, 'success.html', context)
def search_view(request):
    if request.method == 'POST':
        search_query = request.POST.get('s', '')  # Get the search query from the form input
        # Perform the search query using your model
        results = Product.objects.filter(Q(prod_name__icontains=search_query))
        print(results)
        if results:
            return render(request, 'search_results.html', {'results': results})
        
        else:
            message = "No products available starting with '{}'".format(search_query)
            return render(request, 'search_results.html', {'message': message})
    else:
        pass