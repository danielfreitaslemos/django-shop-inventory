from django.shortcuts import get_object_or_404, redirect, render

from .models import Product


def product_lookup(request):
    product = None
    query = request.GET.get("code")

    # 1. Initialize an empty cart in the user's session if it doesn't exist yet
    if "cart" not in request.session:
        request.session["cart"] = []

    if query:
        product = get_object_or_404(Product, product_code=query)

        # 2. Check if the user clicked "Add to Cart"
        if "add_to_cart" in request.GET:
            if product.stock_count > 0:
                # Deduct 1 from database stock
                product.stock_count -= 1
                product.save()

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


def add_product(request):
    if request.method == "POST":
        # 1. Grab data typed into the HTML form fields
        code = request.POST.get("product_code")
        name = request.POST.get("name")
        price = request.POST.get("price")
        stock = request.POST.get("stock_count")

        # 2. Create and save the new product ("The C in CRUD")
        Product.objects.create(
            product_code=code,
            name=name,
            price=price,
            stock_count=stock
        )

        # 3. Redirect back to the lookup scanner to see the new item in action
        return redirect("product_lookup")

    return render(request, "shop/add_product.html")

def manager_dashboard(request):
    # 1. Handle Deletion (The D in CRUD)
    # If the manager clicks delete, a POST request will pass 'delete_id'
    if request.method == "POST" and 'delete_id' in request.POST:
        product_id = request.POST.get('delete_id')
        product_to_delete = get_object_or_404(Product, id=product_id)
        product_to_delete.delete() # Permanently drops the row from the database!
        return redirect('manager_dashboard') # Refresh the page to show it's gone

    # 2. Fetch all products to display on the dashboard
    all_products = Product.objects.all()

    # 3. Define what "Low Stock" means (e.g., fewer than 5 units remaining)
    LOW_STOCK_THRESHOLD = 5

    context = {
        'products': all_products,
        'threshold': LOW_STOCK_THRESHOLD,
    }
    return render(request, 'shop/manager_dashboard.html', context)
