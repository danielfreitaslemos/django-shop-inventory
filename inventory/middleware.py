from django.http import HttpResponseForbidden


class RoleValidationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Combines lines 10 & 12 into a single statement to satisfy Zed's style rules
        if "/manager/" in request.path and (
            not request.user.is_authenticated or not request.user.is_staff
        ):
            # Explicitly define the content variable to eliminate the 'bytes' literal warning
            html_content = "<h1>🚫 403 Access Denied</h1><p>You do not have Manager permissions to view this asset.</p>"
            return HttpResponseForbidden(content=html_content)

        response = self.get_response(request)
        return response
