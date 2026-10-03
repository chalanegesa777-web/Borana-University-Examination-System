# Borana University Examination System

A responsive Django-based online examination system designed for Borana University.

## Features
- Role-based access for admin, instructor, and student
- Course and question bank management
- Exam creation and publishing workflow
- Secure timed exam attempts
- Answer auto-save and review marking
- Automatic and manual grading
- Results dashboards and analytics
- Audit logs and notifications
- CSV report exports and dashboard summaries

## Stack
- Python 3.11+
- Django 4.2+
- SQLite (ready for PostgreSQL migration)

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Admin login
Use the superuser created above.
