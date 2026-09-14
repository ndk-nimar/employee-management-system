"""Forms for the employees app."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import Employee


class StyledAuthenticationForm(AuthenticationForm):
    """Django's own login form, restyled with Bootstrap classes.

    Authentication logic is untouched - only the widgets are customised.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Username",
                "autofocus": True,
                "autocomplete": "username",
            }
        )
        self.fields["password"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        )


class EmployeeForm(forms.ModelForm):
    """ModelForm used by both the Add Employee and Edit Employee pages.

    The field list, field types and validation rules all come from the
    Employee model; this class only customises how the inputs are rendered.
    """

    class Meta:
        model = Employee
        fields = [
            "full_name",
            "gender",
            "date_of_birth",
            "profile_photo",
            "email",
            "phone_number",
            "address",
            "employee_id",
            "department",
            "designation",
            "date_of_joining",
            "salary",
            "employment_status",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "e.g. Nimardeep Kaur"}),
            "email": forms.EmailInput(attrs={"placeholder": "name@company.com"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "+91 98765 43210"}),
            "address": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Street, city, state, postal code"}
            ),
            "employee_id": forms.TextInput(attrs={"placeholder": "EMP-011"}),
            "designation": forms.TextInput(attrs={"placeholder": "e.g. Backend Developer"}),
            "salary": forms.NumberInput(attrs={"step": "1000", "min": "0", "placeholder": "650000"}),
            "date_of_birth": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "date_of_joining": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
        }
        labels = {
            "employee_id": "Employee ID",
            "phone_number": "Phone number",
        }
        help_texts = {
            "profile_photo": "Optional. Leave empty to use a generated initials avatar.",
        }

    # Grouping used by the template so the form renders as three sections
    # without hard-coding every field name in HTML.
    FIELDSETS = [
        ("Personal information", ["full_name", "gender", "date_of_birth", "profile_photo"]),
        ("Contact information", ["email", "phone_number", "address"]),
        (
            "Employment information",
            [
                "employee_id",
                "department",
                "designation",
                "date_of_joining",
                "salary",
                "employment_status",
            ],
        ),
    ]

    # Fields that should take the full width of the form grid.
    WIDE_FIELDS = {"address", "profile_photo"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.Select):
                css_class = "form-select"
            elif isinstance(widget, forms.ClearableFileInput):
                css_class = "form-control"
            elif isinstance(widget, forms.CheckboxInput):
                css_class = "form-check-input"
            else:
                css_class = "form-control"

            existing = widget.attrs.get("class", "")
            widget.attrs["class"] = f"{existing} {css_class}".strip()

            if field.required:
                widget.attrs["required"] = "required"

        # Empty labels for the dropdowns so the user makes a deliberate choice.
        self.fields["gender"].empty_label = "Select gender"
        self.fields["department"].empty_label = "Select department"

    def fieldsets(self):
        """Yield (legend, [BoundField, ...]) pairs for the template."""
        for legend, names in self.FIELDSETS:
            yield legend, [self[name] for name in names]

    def clean_employee_id(self):
        return self.cleaned_data["employee_id"].strip().upper()

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean_full_name(self):
        # Collapse accidental double spaces: "Arjun   Mehta" -> "Arjun Mehta".
        return " ".join(self.cleaned_data["full_name"].split())


class EmployeeFilterForm(forms.Form):
    """Search and filter controls shown above the employee table.

    A plain (non-model) form bound to GET data. Keeping it as a Form means the
    values stay in the inputs after a search, and pagination links can re-use
    the same query string.
    """

    SORT_CHOICES = [
        ("full_name", "Name (A-Z)"),
        ("-full_name", "Name (Z-A)"),
        ("employee_id", "Employee ID"),
        ("-date_of_joining", "Newest joiners"),
        ("date_of_joining", "Earliest joiners"),
        ("-salary", "Highest salary"),
        ("salary", "Lowest salary"),
    ]

    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Search by name, employee ID or email",
                "autocomplete": "off",
            }
        ),
    )
    department = forms.ChoiceField(
        required=False,
        choices=[("", "All departments")] + list(Employee.Department.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        required=False,
        label="Status",
        choices=[("", "All statuses")] + list(Employee.Status.choices),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    sort = forms.ChoiceField(
        required=False,
        choices=SORT_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
