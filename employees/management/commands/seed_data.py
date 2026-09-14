"""`python manage.py seed_data`

Loads ten fictional employees so the dashboard, charts, filters and pagination
have something to show on a fresh database.

Running the command twice is safe: records are matched on the unique
employee_id, so existing rows are skipped rather than duplicated.
"""

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from employees.models import Employee

# All data below is invented for demo purposes.
SAMPLE_EMPLOYEES = [
    {
        "employee_id": "EMP-001",
        "full_name": "Aarav Khanna",
        "gender": Employee.Gender.MALE,
        "date_of_birth": date(1992, 4, 18),
        "email": "aarav.khanna@northwind-demo.com",
        "phone_number": "+91 98110 24567",
        "address": "14 Rosewood Lane, Sector 22, Chandigarh",
        "department": Employee.Department.ENGINEERING,
        "designation": "Senior Backend Developer",
        "date_of_joining": date(2019, 7, 1),
        "salary": Decimal("1450000.00"),
        "employment_status": Employee.Status.ACTIVE,
    },
    {
        "employee_id": "EMP-002",
        "full_name": "Simran Bedi",
        "gender": Employee.Gender.FEMALE,
        "date_of_birth": date(1995, 11, 2),
        "email": "simran.bedi@northwind-demo.com",
        "phone_number": "+91 99887 11223",
        "address": "7B Lakeview Apartments, Ranjit Avenue, Amritsar",
        "department": Employee.Department.ENGINEERING,
        "designation": "Frontend Developer",
        "date_of_joining": date(2021, 2, 15),
        "salary": Decimal("980000.00"),
        "employment_status": Employee.Status.ACTIVE,
    },
    {
        "employee_id": "EMP-003",
        "full_name": "Rohit Nair",
        "gender": Employee.Gender.MALE,
        "date_of_birth": date(1989, 1, 25),
        "email": "rohit.nair@northwind-demo.com",
        "phone_number": "+91 90123 44556",
        "address": "22 Palm Grove, Kakkanad, Kochi",
        "department": Employee.Department.ENGINEERING,
        "designation": "Engineering Manager",
        "date_of_joining": date(2017, 9, 11),
        "salary": Decimal("2100000.00"),
        "employment_status": Employee.Status.ON_LEAVE,
    },
    {
        "employee_id": "EMP-004",
        "full_name": "Priya Deshmukh",
        "gender": Employee.Gender.FEMALE,
        "date_of_birth": date(1993, 6, 30),
        "email": "priya.deshmukh@northwind-demo.com",
        "phone_number": "+91 98220 77341",
        "address": "5 Hillside Road, Kothrud, Pune",
        "department": Employee.Department.HUMAN_RESOURCES,
        "designation": "HR Business Partner",
        "date_of_joining": date(2020, 3, 2),
        "salary": Decimal("870000.00"),
        "employment_status": Employee.Status.ACTIVE,
    },
    {
        "employee_id": "EMP-005",
        "full_name": "Kabir Sethi",
        "gender": Employee.Gender.MALE,
        "date_of_birth": date(1996, 9, 9),
        "email": "kabir.sethi@northwind-demo.com",
        "phone_number": "+91 97654 33210",
        "address": "101 Orchid Residency, Vaishali, Ghaziabad",
        "department": Employee.Department.HUMAN_RESOURCES,
        "designation": "Talent Acquisition Specialist",
        "date_of_joining": date(2022, 8, 22),
        "salary": Decimal("640000.00"),
        "employment_status": Employee.Status.ACTIVE,
    },
    {
        "employee_id": "EMP-006",
        "full_name": "Meera Iyer",
        "gender": Employee.Gender.FEMALE,
        "date_of_birth": date(1990, 12, 14),
        "email": "meera.iyer@northwind-demo.com",
        "phone_number": "+91 96543 21098",
        "address": "30 Temple Street, Adyar, Chennai",
        "department": Employee.Department.FINANCE,
        "designation": "Financial Analyst",
        "date_of_joining": date(2018, 11, 5),
        "salary": Decimal("1150000.00"),
        "employment_status": Employee.Status.ACTIVE,
    },
    {
        "employee_id": "EMP-007",
        "full_name": "Devansh Rao",
        "gender": Employee.Gender.MALE,
        "date_of_birth": date(1987, 3, 21),
        "email": "devansh.rao@northwind-demo.com",
        "phone_number": "+91 90909 12121",
        "address": "8 Jubilee Enclave, Madhapur, Hyderabad",
        "department": Employee.Department.FINANCE,
        "designation": "Payroll Accountant",
        "date_of_joining": date(2016, 5, 30),
        "salary": Decimal("1020000.00"),
        "employment_status": Employee.Status.RESIGNED,
    },
    {
        "employee_id": "EMP-008",
        "full_name": "Ananya Bose",
        "gender": Employee.Gender.FEMALE,
        "date_of_birth": date(1997, 7, 7),
        "email": "ananya.bose@northwind-demo.com",
        "phone_number": "+91 93300 55667",
        "address": "45 Lake Gardens, Kolkata",
        "department": Employee.Department.MARKETING,
        "designation": "Content Marketing Lead",
        "date_of_joining": date(2023, 1, 9),
        "salary": Decimal("790000.00"),
        "employment_status": Employee.Status.ACTIVE,
    },
    {
        "employee_id": "EMP-009",
        "full_name": "Vikram Chadha",
        "gender": Employee.Gender.MALE,
        "date_of_birth": date(1991, 10, 3),
        "email": "vikram.chadha@northwind-demo.com",
        "phone_number": "+91 98150 66778",
        "address": "12 Model Town, Ludhiana",
        "department": Employee.Department.SALES,
        "designation": "Regional Sales Manager",
        "date_of_joining": date(2019, 4, 17),
        "salary": Decimal("1320000.00"),
        "employment_status": Employee.Status.ACTIVE,
    },
    {
        "employee_id": "EMP-010",
        "full_name": "Fatima Sheikh",
        "gender": Employee.Gender.FEMALE,
        "date_of_birth": date(1994, 2, 12),
        "email": "fatima.sheikh@northwind-demo.com",
        "phone_number": "+91 99230 44119",
        "address": "3 Marine Crescent, Bandra West, Mumbai",
        "department": Employee.Department.DESIGN,
        "designation": "Product Designer",
        "date_of_joining": date(2021, 10, 25),
        "salary": Decimal("1080000.00"),
        "employment_status": Employee.Status.ON_LEAVE,
    },
]


class Command(BaseCommand):
    help = "Create ten fictional employees for demo purposes (safe to re-run)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete every existing employee before seeding.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = Employee.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Removed {deleted} existing record(s)."))

        created_count = 0
        skipped_count = 0

        for data in SAMPLE_EMPLOYEES:
            employee, created = Employee.objects.get_or_create(
                employee_id=data["employee_id"],
                defaults=data,
            )
            if created:
                created_count += 1
                self.stdout.write(f"  + {employee.employee_id}  {employee.full_name}")
            else:
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeding complete: {created_count} created, {skipped_count} already present."
            )
        )
