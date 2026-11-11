from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Product, SaleLog

def login_view(request):
    if request.user.is_authenticated:
        return redirect('shop_home')

    error_message = None
    if request.method == "POST":
        user_in = request.POST.get('username')
        pass_in = request.POST.get('password')

        user = authenticate(request, username=user_in, password=pass_in)

        if user is not None:
            login(request, user)
            return redirect('shop_home')
        else:
            error_message = "Invalid username or password. Please try again."

    return render(request, 'shop/login.html', {'error_message': error_message})

# LOGOUT PATHWAY VIEW
def logout_view(request):
    logout(request)
    return redirect('login')

# HOME PATHWAY VIEW
def shop_home(request):
    return render(request, 'shop/home.html')


def product_lookup(request):
    product = None
    query = request.GET.get("code")

    # 1. Initialize an empty cart in the user's session if it doesn't exist yet
    if "cart" not in request.session:
        request.session["cart"] = []

    if query:
        product = Product.objects.filter(product_code=query).first()

        # 2. Check if the user clicked "Add to Cart"
        if product and "add_to_cart" in request.GET:
            if product.stock_count > 0:
                # Deduct 1 from database stock
                product.stock_count -= 1
                product.save()

                SaleLog.objects.create(
                    product=product,
                    product_code=product.product_code,
                    product_name=product.name,
                    quantity=1,
                    total_price=product.price,
                )

                # Copy current cart session data, modify it, and save it back
                current_cart = request.session["cart"]
                current_cart.append(
                    {
                        "name": product.name,
                        "price": float(product.price),
                        "code": product.product_code,
                    }
                )
                request.session["cart"] = current_cart  # Tell Django session changed
            else:
                request.session["stock_error"] = "Out of stock!"

    # 3. Handle clearing the cart entirely
    if "clear_cart" in request.GET:
        request.session["cart"] = []

    # Calculate cart total price dynamically
    cart_total = sum(item["price"] for item in request.session["cart"])

    context = {
        "product": product,
        "cart": request.session["cart"],
        "cart_total": cart_total,
    }
    return render(request, "shop/lookup.html", context)


def sales_history(request):
    # Fetch all logs, ordered by newest transaction first
    logs = SaleLog.objects.all().order_by("-timestamp")

    # Dynamically sum all historical store earnings!
    grand_total_revenue = sum(log.total_price for log in logs)

    context = {"logs": logs, "grand_total": grand_total_revenue}
    return render(request, "shop/sales_history.html", context)


def add_product(request):
    if request.method == "POST":
        # 1. Grab data typed into the HTML form fields
        code = request.POST.get("product_code")
        name = request.POST.get("name")
        price = request.POST.get("price")
        stock = request.POST.get("stock_count")

        # 2. Create and save the new product ("The C in CRUD")
        Product.objects.create(
            product_code=code, name=name, price=price, stock_count=stock
        )

        # 3. Redirect back to the lookup scanner to see the new item in action
        return redirect("product_lookup")

    return render(request, "shop/add_product.html")


def manager_dashboard(request):
    # 1. Handle Deletion (The D in CRUD)
    # If the manager clicks delete, a POST request will pass 'delete_id'
    if request.method == "POST" and "delete_id" in request.POST:
        product_id = request.POST.get("delete_id")
        product_to_delete = get_object_or_404(Product, id=product_id)
        product_to_delete.delete()  # Permanently drops the row from the database!
        return redirect("manager_dashboard")  # Refresh the page to show it's gone

    # 2. Fetch all products to display on the dashboard
    all_products = Product.objects.all()

    # 3. Define what "Low Stock" means (e.g., fewer than 5 units remaining)
    LOW_STOCK_THRESHOLD = 5

    context = {
        "products": all_products,
        "threshold": LOW_STOCK_THRESHOLD,
    }
    return render(request, "shop/manager_dashboard.html", context)


# EDIT VIEW
def edit_product(request, product_id):
    # Fetch the specific product using its unique database ID row number
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        # Overwrite the old values with whatever the manager typed into the edit form
        product.product_code = request.POST.get("product_code")
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.stock_count = request.POST.get("stock_count")

        product.save()  # <--- Saves the updated row back to SQLite
        return redirect("manager_dashboard")  # Send them back to the dashboard

    return render(request, "shop/edit_product.html", {"product": product})


def shop_home(request):
    return render(request, "shop/home.html")
