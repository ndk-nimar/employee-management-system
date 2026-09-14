# Employee Management System

A Django web application for managing an organisation's employee records: a
statistics dashboard, a searchable employee directory, full create / read /
update / delete support, and authentication so that only signed-in staff can
see or change data.

Built with Django's MVT (Model–View–Template) pattern, the Django ORM on top of
SQLite, Django ModelForms for validation, and a custom Bootstrap 5 theme for the
interface.

---

## Overview

The app is a small internal HR tool. After signing in, a user lands on a
dashboard showing headcount by status and by department, then moves into the
employee directory to search, filter, sort, page through records, and open an
individual profile to edit or delete it.

Everything is server-rendered: filtering and pagination happen in the database
through the ORM, not in the browser. JavaScript is used only for interface
details (mobile sidebar, toast dismissal, the delete confirmation modal, the
password reveal on the login page) and for drawing two Chart.js charts from data
that Django passes into the page.

---

## Features

**Dashboard**
- Time-aware greeting and four statistic cards: total, active, on leave, resigned
- Bar chart of headcount by department (Chart.js, data from the database)
- Doughnut chart of employment status, plus average salary and total payroll
- List of the five most recently added employees
- Department headcount list and quick action links

**Employee directory**
- Table with avatar, employee ID, name, department, designation, contact
  details, status badge, joining date and row actions
- Search across name, employee ID and email
- Filters for department and employment status (they combine with search)
- Sorting by name, employee ID, joining date or salary
- Django pagination, eight employees per page, filters preserved across pages
- Separate empty states for "no employees yet" and "no search results"

**Employee records**
- Add and edit through a single Django ModelForm, grouped into Personal,
  Contact and Employment sections
- Validation errors shown next to the field, with submitted data preserved
- Optional profile photo upload; an existing photo is kept if no new file is
  chosen; employees without a photo get a generated initials avatar
- Profile page with the full record, including created / updated timestamps
- Deletion via POST only, with a confirmation modal in the table and a full
  confirmation page at its own URL

**Platform**
- Django authentication with a custom login page; every application view is
  protected with `@login_required`
- Django messages framework, rendered as auto-dismissing toasts
- Custom 404 and 500 pages styled like the rest of the app
- Employee model registered in the Django admin with list display, search,
  filters, ordering and grouped edit fieldsets
- `seed_data` management command that loads ten fictional employees
- 18 automated tests covering models, forms, authentication and every view

---

## Tech stack

| Layer | Choice |
|---|---|
| Language | Python 3.10+ |
| Framework | Django 5.x / 6.x |
| Database | SQLite (via the Django ORM) |
| Forms | Django ModelForms |
| Auth | Django's built-in authentication |
| Templates | Django template language with inheritance |
| Styling | HTML5, CSS3, Bootstrap 5, Bootstrap Icons |
| Charts | Chart.js 4 |
| Images | Pillow (required by `ImageField`) |

---

## Project structure

```
employee_management/
├── manage.py
├── requirements.txt
├── README.md
├── .gitignore
├── db.sqlite3                      # created by `migrate`
│
├── employee_management/            # project package
│   ├── __init__.py
│   ├── settings.py                 # apps, templates, static/media, auth redirects
│   ├── urls.py                     # admin, login/logout, app include, error handlers
│   ├── asgi.py
│   └── wsgi.py
│
├── employees/                      # application
│   ├── __init__.py
│   ├── admin.py                    # EmployeeAdmin configuration
│   ├── apps.py
│   ├── forms.py                    # EmployeeForm, EmployeeFilterForm, login form styling
│   ├── models.py                   # Employee model, validation, avatar helpers
│   ├── urls.py                     # app URL patterns (namespace: employees)
│   ├── views.py                    # dashboard, list, detail, create, update, delete
│   ├── tests.py                    # 18 tests
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py        # python manage.py seed_data
│   ├── templates/employees/
│   │   ├── dashboard.html
│   │   ├── employee_list.html
│   │   ├── employee_detail.html
│   │   ├── employee_form.html
│   │   ├── employee_confirm_delete.html
│   │   └── partials/
│   │       ├── avatar.html
│   │       ├── status_badge.html
│   │       ├── messages.html
│   │       └── pagination.html
│   └── static/employees/
│       ├── css/style.css
│       └── js/
│           ├── script.js           # sidebar, toasts, delete modal, password toggle
│           └── charts.js           # Chart.js setup
│
└── templates/
    ├── base.html                   # sidebar + topbar + messages + content block
    ├── 404.html
    ├── 500.html
    └── registration/login.html
```

---

## Installation

Requires Python 3.10 or newer.

```bash
# 1. create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 2. install dependencies
pip install -r requirements.txt

# 3. create the database tables
python manage.py migrate

# 4. create your admin account (you choose the username and password)
python manage.py createsuperuser

# 5. load ten fictional employees so the dashboard has data
python manage.py seed_data

# 6. start the development server
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. You will be redirected to the login page.

The Django admin is at <http://127.0.0.1:8000/admin/>.

Bootstrap, Bootstrap Icons, Chart.js and the web font are loaded from a CDN, so
the first page load needs an internet connection.

---

## Login

There is no public sign-up page, which is deliberate: accounts are created by an
administrator. Create the first one from the terminal:

```bash
python manage.py createsuperuser
```

Django will prompt for a username, an optional email and a password. Use those
credentials on the login page. No password is stored in this repository, and
Django stores only a salted hash of it in the database.

To add more staff accounts later, use the Users section of the Django admin.

---

## Screens and features

**Login** — a two-panel page. Failed attempts show a single generic error (the
app never reveals whether the username or the password was wrong).

**Dashboard** (`/`) — statistic cards, department bar chart, status doughnut
chart, recently added employees, department headcount and quick actions. Every
number comes from an ORM aggregate query executed when the page is requested.

**Employees** (`/employees/`) — the directory. The search box matches name,
employee ID or email; the two dropdowns filter by department and status; the
sort dropdown reorders results. All of them combine into one queryset and can be
shared as a URL, because the state lives in the query string.

**Employee profile** (`/employees/<id>/`) — the full record in grouped cards,
with edit and delete actions.

**Add / edit** (`/employees/add/`, `/employees/<id>/edit/`) — one ModelForm
rendered in three sections. Invalid submissions come back with the data intact
and errors under the relevant fields.

**Delete** (`/employees/<id>/delete/`) — a confirmation page, plus a modal
shortcut from the table. Both submit a POST request with a CSRF token.

**Django admin** (`/admin/`) — the same records with admin-level tooling:
searching, filtering by department, status, gender and joining date, and a date
drill-down.

---

## Database

The project uses SQLite, the file-based database bundled with Python, so there
is nothing to install or configure. `python manage.py migrate` creates
`db.sqlite3` in the project root.

Tables are described in Python by the `Employee` model rather than in SQL.
`makemigrations` turns model changes into migration files and `migrate` applies
them, which keeps the schema versioned alongside the code. Queries are written
through the ORM (`Employee.objects.filter(...)`, `annotate(Count("id"))`), so
Django builds the SQL and escapes parameters, which also rules out SQL
injection through the search box.

Switching to PostgreSQL later would mean changing the `DATABASES` setting and
re-running `migrate` — the model and view code would not change.

---

## Security notes

- CSRF protection on every form (`{% csrf_token %}` plus Django's middleware)
- Deletion only happens on POST; a GET request renders the confirmation page
- All application views are behind `@login_required`
- Logout is POST-only, so a link cannot sign a user out
- Passwords are hashed by Django; no credentials are stored in the repository
- User input reaches the database only through the ORM and form validation
- Uploaded photos are written to `MEDIA_ROOT`, outside the code directories

**Before deploying**, set `DEBUG = False`, move `SECRET_KEY` to an environment
variable, add the real domain to `ALLOWED_HOSTS`, serve static files with
`collectstatic` behind a web server, and hand media file serving to that server
instead of Django.

---

## Running the tests

```bash
python manage.py test
```

Eighteen tests cover model validation and helpers, form validation, login
protection, dashboard statistics, search, filtering, create, update and both
halves of the delete behaviour.

---

## Future improvements

Not implemented — ideas for a next version:

- Role-based access (HR manager vs. read-only viewer)
- Export the filtered employee list to CSV or Excel
- Email notifications when a record changes
- Leave and attendance tracking
- Advanced analytics: salary bands, attrition trends, headcount over time
- Deployment on PostgreSQL with static files on object storage
- A REST API for other internal tools to consume
