"""Database models for the Employee Management System."""

from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.urls import reverse


class Employee(models.Model):
    """A single employee record.

    One row in the `employees_employee` table. Everything the HR user sees in
    the dashboard, the table and the profile page comes from this model.
    """

    class Gender(models.TextChoices):
        FEMALE = "F", "Female"
        MALE = "M", "Male"
        OTHER = "O", "Other"

    class Department(models.TextChoices):
        ENGINEERING = "Engineering", "Engineering"
        HUMAN_RESOURCES = "Human Resources", "Human Resources"
        FINANCE = "Finance", "Finance"
        MARKETING = "Marketing", "Marketing"
        SALES = "Sales", "Sales"
        OPERATIONS = "Operations", "Operations"
        DESIGN = "Design", "Design"
        SUPPORT = "Customer Support", "Customer Support"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ON_LEAVE = "ON_LEAVE", "On Leave"
        RESIGNED = "RESIGNED", "Resigned"

    # --- Validators -----------------------------------------------------
    employee_id_validator = RegexValidator(
        regex=r"^[A-Za-z0-9\-]{3,20}$",
        message="Use 3-20 letters, numbers or hyphens (for example EMP-001).",
    )
    phone_validator = RegexValidator(
        regex=r"^\+?[0-9\s\-]{7,20}$",
        message="Enter a valid phone number, for example +91 98765 43210.",
    )

    # --- Identity -------------------------------------------------------
    employee_id = models.CharField(
        "employee ID",
        max_length=20,
        unique=True,
        validators=[employee_id_validator],
        help_text="Unique company identifier, for example EMP-001.",
    )
    full_name = models.CharField(max_length=120)
    gender = models.CharField(max_length=1, choices=Gender.choices)
    date_of_birth = models.DateField()

    # --- Contact --------------------------------------------------------
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, validators=[phone_validator])
    address = models.TextField(blank=True)

    # --- Employment -----------------------------------------------------
    department = models.CharField(max_length=40, choices=Department.choices)
    designation = models.CharField(max_length=80)
    date_of_joining = models.DateField()
    salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Annual gross salary.",
    )
    employment_status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    profile_photo = models.ImageField(upload_to="employee_photos/", blank=True, null=True)

    # --- Bookkeeping ----------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "employee"
        verbose_name_plural = "employees"
        indexes = [
            models.Index(fields=["department"]),
            models.Index(fields=["employment_status"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"

    def get_absolute_url(self):
        return reverse("employees:employee_detail", args=[self.pk])

    # --- Validation -----------------------------------------------------
    def clean(self):
        """Cross-field rules that a single field validator cannot express.

        Called automatically by ModelForm.is_valid(), so the messages show up
        next to the right input on the add/edit pages.
        """
        errors = {}
        today = date.today()

        if self.date_of_birth and self.date_of_birth >= today:
            errors["date_of_birth"] = "Date of birth must be in the past."

        if self.date_of_birth and self.date_of_joining:
            if self.date_of_joining <= self.date_of_birth:
                errors["date_of_joining"] = (
                    "Date of joining must be after the date of birth."
                )
            elif self._years_between(self.date_of_birth, self.date_of_joining) < 18:
                errors["date_of_joining"] = (
                    "Employee must be at least 18 years old on the joining date."
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Employee IDs are stored uppercase so that searching and the
        # uniqueness check behave predictably.
        if self.employee_id:
            self.employee_id = self.employee_id.upper().strip()
        super().save(*args, **kwargs)

    # --- Display helpers used by the templates --------------------------
    @staticmethod
    def _years_between(start, end):
        return end.year - start.year - ((end.month, end.day) < (start.month, start.day))

    @property
    def initials(self):
        """'Nimardeep Kaur' -> 'NK'. Used for the generated avatar."""
        parts = [p for p in self.full_name.split() if p]
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    @property
    def avatar_color(self):
        """A stable colour per employee, picked from a small curated palette.

        Deterministic (same employee always gets the same colour) and computed
        locally, so no external avatar service is needed.
        """
        palette = [
            "#1f6f63",
            "#2a5d9f",
            "#7a4bb0",
            "#a8562f",
            "#b0893a",
            "#3d6b3a",
            "#8c3f5b",
            "#3f5a8c",
        ]
        seed = sum(ord(char) for char in (self.employee_id or self.full_name or "?"))
        return palette[seed % len(palette)]

    @property
    def status_css(self):
        """Badge modifier class used in the templates."""
        return {
            self.Status.ACTIVE: "status-active",
            self.Status.ON_LEAVE: "status-leave",
            self.Status.RESIGNED: "status-resigned",
        }.get(self.employment_status, "status-active")

    @property
    def age(self):
        if not self.date_of_birth:
            return None
        return self._years_between(self.date_of_birth, date.today())

    @property
    def tenure_years(self):
        if not self.date_of_joining:
            return None
        return max(self._years_between(self.date_of_joining, date.today()), 0)
