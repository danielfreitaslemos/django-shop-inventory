from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .models import PixConfig, Product, SaleLog
from .pix_utils import generate_pix_payload, generate_pix_svg
from io import BytesIO
from datetime import datetime
from django.http import HttpResponse
from reportlab.pdfgen import canvas



def login_view(request):
    if request.user.is_authenticated:
        return redirect("shop_home")

    error_message = None
    if request.method == "POST":
        user_in = request.POST.get("username")
        pass_in = request.POST.get("password")

        user = authenticate(request, username=user_in, password=pass_in)

        if user is not None:
            login(request, user)
            return redirect("shop_home")
        else:
            error_message = "Invalid username or password. Please try again."

    return render(request, "shop/login.html", {"error_message": error_message})


# LOGOUT PATHWAY VIEW
def logout_view(request):
    logout(request)
    return redirect("login")


# HOME PATHWAY VIEW
def shop_home(request):
    return render(request, "shop/home.html")


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

    pix_svg = None
    pix_copia_colaa = None
    pix_config = PixConfig.objects.first()

    if cart_total > 0 and pix_config:
        pix_copia_colaa = generate_pix_payload(
            pix_config.pix_key,
            pix_config.merchant_name,
            pix_config.merchant_city,
            cart_total,
        )
        pix_svg = generate_pix_svg(pix_copia_colaa)

    context = {
        "product": product,
        "cart": request.session["cart"],
        "cart_total": cart_total,
        "pix_svg": pix_svg,
        "pix_copia_cola": pix_copia_colaa,
        "pix_config": pix_config,
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


def pix_settings(request):
    config = PixConfig.objects.first()
    saved = False

    if request.method == "POST":
        pix_key = request.POST.get("pix_key")
        merchant_name = request.POST.get("merchant_name")
        merchant_city = request.POST.get("merchant_city")

        if config:
            config.pix_key = pix_key
            config.merchant_name = merchant_name
            config.merchant_city = merchant_city
            config.save()
        else:
            config = PixConfig.objects.create(
                pix_key=pix_key,
                merchant_name=merchant_name,
                merchant_city=merchant_city,
            )
        saved = True

    return render(request, "shop/pix_settings.html", {"config": config, "saved": saved})

def manage_cashiers(request):
    message = None
    error = None

    if request.method == "POST":
        # Handle deleting an existing cashier
        if "delete_user_id" in request.POST:
            user_id = request.POST.get("delete_user_id")
            cashier = User.objects.filter(id=user_id, is_superuser=False).first()
            if cashier:
                cashier.delete()
                message = "Cashier account removed successfully."

        # Handle creating a new cashier
        elif "create_cashier" in request.POST:
            username = request.POST.get("username").strip()
            password = request.POST.get("password")

            if User.objects.filter(username=username).exists():
                error = f"Username '{username}' is already taken."
            elif len(password) < 6:
                error = "Password must be at least 6 characters long."
            else:
                User.objects.create_user(username=username, password=password)
                message = f"Cashier '{username}' created successfully!"

    # Fetch only standard cashier accounts (exclude managers/superusers)
    cashiers = User.objects.filter(is_superuser=False).order_by("-date_joined")

    return render(request, "shop/manage_cashiers.html", {
        "cashiers": cashiers,
        "message": message,
        "error": error
    })


# PDF RECEIPT
def download_receipt(request):
    cart = request.session.get('cart', [])
    if not cart:
        return redirect('product_lookup')

    # Pull store name from PixConfig if available
    pix_config = PixConfig.objects.first()
    store_name = pix_config.merchant_name if pix_config else "SHOP OS"

    # Create an in-memory PDF buffer (80mm thermal receipt width ~ 226pt)
    buffer = BytesIO()
    page_height = 220 + (len(cart) * 18)
    p = canvas.Canvas(buffer, pagesize=(226, page_height))

    y = page_height - 25

    # Store Header
    p.setFont("Helvetica-Bold", 12)
    p.drawCentredString(113, y, store_name.upper())
    y -= 15

    p.setFont("Helvetica", 8)
    p.drawCentredString(113, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 12
    p.drawCentredString(113, y, f"Cashier: {request.user.username}")
    y -= 15

    p.line(15, y, 211, y)
    y -= 15

    # Itemized List
    p.setFont("Helvetica-Bold", 8)
    p.drawString(15, y, "ITEM")
    p.drawRightString(211, y, "PRICE")
    y -= 14

    p.setFont("Helvetica", 8)
    total = 0.0
    for item in cart:
        name = item['name'][:22]
        price = float(item['price'])
        total += price
        p.drawString(15, y, f"{name} ({item['code']})")
        p.drawRightString(211, y, f"R$ {price:.2f}")
        y -= 14

    y -= 4
    p.line(15, y, 211, y)
    y -= 18

    # Total Due
    p.setFont("Helvetica-Bold", 10)
    p.drawString(15, y, "TOTAL PAID:")
    p.drawRightString(211, y, f"R$ {total:.2f}")
    y -= 25

    # Footer
    p.setFont("Helvetica-Oblique", 8)
    p.drawCentredString(113, y, "Thank you for shopping with us!")

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    filename = f"receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
