from django.shortcuts import redirect, render


class ShopSecurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # 1. Allow public access to login, admin, and static CSS files
        if (
            path.startswith("/login/")
            or path.startswith("/admin/")
            or path.startswith("/static/")
        ):
            return self.get_response(request)

        # 2. Block unauthenticated users globally
        if not request.user.is_authenticated:
            return redirect("login")

        # 3. Block non-managers from accessing any /manager/ URLs
        if path.startswith("/manager/") and not request.user.is_superuser:
            return render(request, "shop/403.html", status=403)

        # 4. Let valid requests pass through to the views
        return self.get_response(request)
