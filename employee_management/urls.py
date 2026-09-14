"""
Root URL configuration.

Routes:
    /admin/      -> Django admin
    /login/      -> login page (django.contrib.auth)
    /logout/     -> logout (POST only)
    /            -> the `employees` app (dashboard + employee CRUD)
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from employees.views import AppLoginView, app_logout

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", AppLoginView.as_view(), name="login"),
    path("logout/", app_logout, name="logout"),
    path("", include("employees.urls", namespace="employees")),
]

# During development Django serves uploaded profile photos itself.
# A real deployment would hand this job to nginx / a CDN instead.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error pages (templates/404.html and templates/500.html).
handler404 = "employees.views.page_not_found"
handler500 = "employees.views.server_error"
