"""Django admin configuration.

The admin is a second, staff-only way into the same data, useful for bulk
corrections that the main UI does not cover.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "employee_id",
        "full_name",
        "department",
        "designation",
        "email",
        "status_badge",
        "date_of_joining",
        "salary",
    )
    list_display_links = ("employee_id", "full_name")
    search_fields = ("employee_id", "full_name", "email", "phone_number", "designation")
    list_filter = ("department", "employment_status", "gender", "date_of_joining")
    ordering = ("full_name",)
    list_per_page = 25
    date_hierarchy = "date_of_joining"
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Personal information", {"fields": ("full_name", "gender", "date_of_birth", "profile_photo")}),
        ("Contact information", {"fields": ("email", "phone_number", "address")}),
        (
            "Employment information",
            {
                "fields": (
                    "employee_id",
                    "department",
                    "designation",
                    "date_of_joining",
                    "salary",
                    "employment_status",
                )
            },
        ),
        ("Record history", {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Status", ordering="employment_status")
    def status_badge(self, obj):
        colors = {
            Employee.Status.ACTIVE: "#1f6f63",
            Employee.Status.ON_LEAVE: "#b0893a",
            Employee.Status.RESIGNED: "#8a8f98",
        }
        return format_html(
            '<span style="color:{}; font-weight:600;">{}</span>',
            colors.get(obj.employment_status, "#444"),
            obj.get_employment_status_display(),
        )
