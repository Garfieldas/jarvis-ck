from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import NoReverseMatch, reverse


class RestrictAdminMiddleware:
    """Restrict admin pages to authenticated superusers only."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_url = reverse("admin:index")

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Restrict all admin endpoints, not only the index page.
        if not request.path.startswith(self.admin_url):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect("admin:login")

        if not request.user.is_superuser:
            try:
                return redirect("home")
            except NoReverseMatch:
                return redirect("/")

        return self.get_response(request)
