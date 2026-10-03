# Borana University Examination System

A modern Django-based online examination platform for Borana University. This project includes role-based access control, course management, question bank, exam workflows, timed attempts, grading, notifications, reports, and audit logs.

## Features
- Administrator, instructor, and student roles
- Course and enrollment management
- Reusable question bank with difficulty, topic, category, and status
- Exam builder with scheduling, timing, and validation
- Randomized question and answer ordering
- Timed exam attempts with server-side validation
- Auto-save and mark-for-review support
- Automated/manual grading and result analytics
- Notifications and audit logs
- CSV export and reporting pages
- Responsive UI designed for university use

## Tech stack
- Python 3.11+
- Django 4.2+
- SQLite for local development

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Demo roles
- Admin: create superuser and log in
- Instructor: create via Django admin or registration flow
- Student: register and enroll

## Notes
This project is suitable for a final year Bachelor of Computer Science project and is intentionally built using a simple but professional Django architecture.
