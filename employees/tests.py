"""Tests for the employees app.

Run with:  python manage.py test
"""

from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .forms import EmployeeForm
from .models import Employee


def employee_payload(**overrides):
    """Valid POST data for the employee form."""
    data = {
        "full_name": "Asha Verma",
        "gender": Employee.Gender.FEMALE,
        "date_of_birth": "1994-03-12",
        "email": "asha.verma@northwind-demo.com",
        "phone_number": "+91 98765 11111",
        "address": "21 Green Park, Delhi",
        "employee_id": "EMP-501",
        "department": Employee.Department.ENGINEERING,
        "designation": "QA Engineer",
        "date_of_joining": "2021-01-04",
        "salary": "720000",
        "employment_status": Employee.Status.ACTIVE,
    }
    data.update(overrides)
    return data


class EmployeeModelTests(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            employee_id="EMP-101",
            full_name="Nimardeep Kaur",
            gender=Employee.Gender.FEMALE,
            date_of_birth=date(1995, 8, 20),
            email="nimardeep.kaur@northwind-demo.com",
            phone_number="+91 90000 11111",
            department=Employee.Department.FINANCE,
            designation="Analyst",
            date_of_joining=date(2020, 5, 1),
            salary=Decimal("900000.00"),
        )

    def test_str_representation(self):
        self.assertEqual(str(self.employee), "Nimardeep Kaur (EMP-101)")

    def test_initials_for_generated_avatar(self):
        self.assertEqual(self.employee.initials, "NK")

    def test_employee_id_is_stored_uppercase(self):
        employee = Employee.objects.create(
            employee_id="emp-102",
            full_name="Rahul Sood",
            gender=Employee.Gender.MALE,
            date_of_birth=date(1990, 1, 1),
            email="rahul.sood@northwind-demo.com",
            phone_number="+91 90000 22222",
            department=Employee.Department.SALES,
            designation="Executive",
            date_of_joining=date(2019, 2, 2),
            salary=Decimal("500000.00"),
        )
        self.assertEqual(employee.employee_id, "EMP-102")

    def test_joining_date_cannot_precede_birth_date(self):
        self.employee.date_of_joining = date(1990, 1, 1)
        with self.assertRaises(ValidationError):
            self.employee.full_clean()


class EmployeeFormTests(TestCase):
    def test_valid_payload(self):
        self.assertTrue(EmployeeForm(data=employee_payload()).is_valid())

    def test_negative_salary_is_rejected(self):
        form = EmployeeForm(data=employee_payload(salary="-100"))
        self.assertFalse(form.is_valid())
        self.assertIn("salary", form.errors)

    def test_invalid_phone_is_rejected(self):
        form = EmployeeForm(data=employee_payload(phone_number="call me"))
        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_duplicate_employee_id_is_rejected(self):
        EmployeeForm(data=employee_payload()).save()
        form = EmployeeForm(data=employee_payload(email="other@northwind-demo.com"))
        self.assertFalse(form.is_valid())
        self.assertIn("employee_id", form.errors)


class AuthenticationTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("employees:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_logout_requires_post(self):
        User.objects.create_user("hr", password="TestPass!2345")
        self.client.login(username="hr", password="TestPass!2345")
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        self.assertEqual(self.client.post(reverse("logout")).status_code, 302)


class EmployeeViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("hr", password="TestPass!2345")
        cls.alpha = Employee.objects.create(
            employee_id="EMP-201",
            full_name="Ishaan Roy",
            gender=Employee.Gender.MALE,
            date_of_birth=date(1993, 6, 1),
            email="ishaan.roy@northwind-demo.com",
            phone_number="+91 90000 33333",
            department=Employee.Department.ENGINEERING,
            designation="Developer",
            date_of_joining=date(2020, 1, 6),
            salary=Decimal("1000000.00"),
        )
        cls.beta = Employee.objects.create(
            employee_id="EMP-202",
            full_name="Tara Menon",
            gender=Employee.Gender.FEMALE,
            date_of_birth=date(1991, 9, 15),
            email="tara.menon@northwind-demo.com",
            phone_number="+91 90000 44444",
            department=Employee.Department.MARKETING,
            designation="Brand Manager",
            date_of_joining=date(2018, 11, 19),
            salary=Decimal("1200000.00"),
            employment_status=Employee.Status.ON_LEAVE,
        )

    def setUp(self):
        self.client.force_login(self.user)

    def test_dashboard_statistics(self):
        response = self.client.get(reverse("employees:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_employees"], 2)
        self.assertEqual(response.context["active_count"], 1)
        self.assertEqual(response.context["on_leave_count"], 1)
        self.assertEqual(len(response.context["department_labels"]), 2)

    def test_search_matches_name_id_and_email(self):
        url = reverse("employees:employee_list")
        for term in ["Tara", "EMP-202", "tara.menon@northwind-demo.com"]:
            response = self.client.get(url, {"q": term})
            self.assertEqual(response.context["total_matches"], 1, term)

    def test_filters_combine(self):
        response = self.client.get(
            reverse("employees:employee_list"),
            {"department": Employee.Department.ENGINEERING, "status": Employee.Status.ACTIVE},
        )
        self.assertEqual(response.context["total_matches"], 1)

    def test_create_employee(self):
        response = self.client.post(
            reverse("employees:employee_create"), employee_payload(), follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Employee.objects.filter(employee_id="EMP-501").exists())

    def test_update_employee(self):
        response = self.client.post(
            reverse("employees:employee_update", args=[self.alpha.pk]),
            employee_payload(
                employee_id=self.alpha.employee_id,
                email=self.alpha.email,
                full_name="Ishaan Roy",
                designation="Senior Developer",
            ),
            follow=True,
        )
        self.alpha.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.alpha.designation, "Senior Developer")

    def test_get_request_never_deletes(self):
        self.client.get(reverse("employees:employee_delete", args=[self.alpha.pk]))
        self.assertTrue(Employee.objects.filter(pk=self.alpha.pk).exists())

    def test_post_deletes(self):
        self.client.post(reverse("employees:employee_delete", args=[self.alpha.pk]))
        self.assertFalse(Employee.objects.filter(pk=self.alpha.pk).exists())

    def test_missing_employee_returns_404(self):
        response = self.client.get(reverse("employees:employee_detail", args=[999999]))
        self.assertEqual(response.status_code, 404)
