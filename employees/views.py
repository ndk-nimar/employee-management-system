"""Views for the employees app.

Every view except the login page is wrapped in @login_required, so an
anonymous visitor is redirected to /login/?next=... instead of seeing data.
"""

from datetime import datetime

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import EmployeeFilterForm, EmployeeForm, StyledAuthenticationForm
from .models import Employee

EMPLOYEES_PER_PAGE = 8


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


class AppLoginView(LoginView):
    """Django's LoginView with our template, our styled form and a message."""

    template_name = "registration/login.html"
    form_class = StyledAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Welcome back, {self.request.user.username}.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Those credentials did not match our records.")
        return super().form_invalid(form)


@require_POST
def app_logout(request):
    """Log the user out. POST only, which is what Django 5+ expects anyway."""
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect("login")


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


def _greeting():
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


@login_required
def dashboard(request):
    """Aggregate statistics for the landing page.

    All numbers are calculated by the database through the Django ORM
    (COUNT / AVG / SUM), not in Python, so the page stays fast as the table
    grows.
    """
    employees = Employee.objects.all()

    status_counts = {
        row["employment_status"]: row["total"]
        for row in employees.values("employment_status").annotate(total=Count("id"))
    }

    department_rows = (
        employees.values("department")
        .annotate(total=Count("id"))
        .order_by("-total", "department")
    )
    salary_stats = employees.aggregate(total=Sum("salary"), average=Avg("salary"))

    context = {
        "greeting": _greeting(),
        "total_employees": employees.count(),
        "active_count": status_counts.get(Employee.Status.ACTIVE, 0),
        "on_leave_count": status_counts.get(Employee.Status.ON_LEAVE, 0),
        "resigned_count": status_counts.get(Employee.Status.RESIGNED, 0),
        "department_rows": department_rows,
        "recent_employees": employees.order_by("-created_at")[:5],
        "average_salary": salary_stats["average"] or 0,
        "total_payroll": salary_stats["total"] or 0,
        # Chart.js reads these through {{ ...|json_script }} in the template.
        "department_labels": [row["department"] for row in department_rows],
        "department_values": [row["total"] for row in department_rows],
        "status_labels": ["Active", "On Leave", "Resigned"],
        "status_values": [
            status_counts.get(Employee.Status.ACTIVE, 0),
            status_counts.get(Employee.Status.ON_LEAVE, 0),
            status_counts.get(Employee.Status.RESIGNED, 0),
        ],
        "page_title": "Dashboard",
        "active_nav": "dashboard",
    }
    return render(request, "employees/dashboard.html", context)


# ---------------------------------------------------------------------------
# Employee list: search + filter + sort + pagination
# ---------------------------------------------------------------------------


@login_required
def employee_list(request):
    """Employee directory.

    The search box, both dropdown filters and the sort selector all build one
    queryset. Because a queryset is lazy, the filters chain together and a
    single SQL query runs when the page is rendered.
    """
    form = EmployeeFilterForm(request.GET or None)
    employees = Employee.objects.all()

    query = department = status = ""
    sort = "full_name"

    if form.is_valid():
        query = form.cleaned_data.get("q", "").strip()
        department = form.cleaned_data.get("department", "")
        status = form.cleaned_data.get("status", "")
        sort = form.cleaned_data.get("sort") or "full_name"

    if query:
        employees = employees.filter(
            Q(full_name__icontains=query)
            | Q(employee_id__icontains=query)
            | Q(email__icontains=query)
        )
    if department:
        employees = employees.filter(department=department)
    if status:
        employees = employees.filter(employment_status=status)

    allowed_sorts = {choice for choice, _ in EmployeeFilterForm.SORT_CHOICES}
    if sort not in allowed_sorts:
        sort = "full_name"
    employees = employees.order_by(sort)

    paginator = Paginator(employees, EMPLOYEES_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Query string without `page`, so pagination links keep the active filters.
    params = request.GET.copy()
    params.pop("page", None)
    querystring = params.urlencode()

    context = {
        "form": form,
        "page_obj": page_obj,
        "employees": page_obj.object_list,
        "paginator": paginator,
        "total_matches": paginator.count,
        "querystring": querystring,
        "has_filters": bool(query or department or status),
        "page_title": "Employees",
        "active_nav": "employees",
    }
    return render(request, "employees/employee_list.html", context)


# ---------------------------------------------------------------------------
# Employee CRUD
# ---------------------------------------------------------------------------


@login_required
def employee_detail(request, pk):
    """Profile page. get_object_or_404 turns a bad id into our 404 page."""
    employee = get_object_or_404(Employee, pk=pk)
    return render(
        request,
        "employees/employee_detail.html",
        {
            "employee": employee,
            "page_title": employee.full_name,
            "active_nav": "employees",
        },
    )


@login_required
def employee_create(request):
    if request.method == "POST":
        # request.FILES carries the uploaded profile photo.
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f"{employee.full_name} was added to the directory.")
            return redirect(employee.get_absolute_url())
        messages.error(request, "Please correct the highlighted fields.")
    else:
        form = EmployeeForm()

    return render(
        request,
        "employees/employee_form.html",
        {
            "form": form,
            "employee": None,
            "form_heading": "Add employee",
            "form_subheading": "Create a new record in the employee directory.",
            "submit_label": "Save employee",
            "page_title": "Add employee",
            "active_nav": "add",
        },
    )


@login_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == "POST":
        # `instance=employee` makes this an update instead of an insert.
        # If no new photo is posted, the existing file is kept untouched.
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f"{employee.full_name}'s record was updated.")
            return redirect(employee.get_absolute_url())
        messages.error(request, "Please correct the highlighted fields.")
    else:
        form = EmployeeForm(instance=employee)

    return render(
        request,
        "employees/employee_form.html",
        {
            "form": form,
            "employee": employee,
            "form_heading": "Edit employee",
            "form_subheading": f"Update the record for {employee.full_name}.",
            "submit_label": "Save changes",
            "page_title": f"Edit {employee.full_name}",
            "active_nav": "employees",
        },
    )


@login_required
def employee_delete(request, pk):
    """Deletion is only performed on POST.

    A GET request just renders the confirmation page, so a crawler, a
    prefetching browser or an accidental link click can never remove a record.
    """
    employee = get_object_or_404(Employee, pk=pk)

    if request.method == "POST":
        name = employee.full_name
        employee.delete()
        messages.success(request, f"{name} was removed from the directory.")
        return redirect("employees:employee_list")

    return render(
        request,
        "employees/employee_confirm_delete.html",
        {
            "employee": employee,
            "page_title": f"Delete {employee.full_name}",
            "active_nav": "employees",
        },
    )


# ---------------------------------------------------------------------------
# Error handlers (wired up in employee_management/urls.py)
# ---------------------------------------------------------------------------


def page_not_found(request, exception):
    return render(request, "404.html", status=404)


def server_error(request):
    return render(request, "500.html", status=500)
