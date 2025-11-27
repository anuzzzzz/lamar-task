# Intake Activity Feed

A simple internal tool for pharmacy intake teams to track prescription activity.

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
cd intake
python manage.py migrate

# Create admin user (optional, for adding test data)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

## Usage

- Dashboard: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Running Tests

```bash
cd intake
python manage.py test workflow
```

## Features

- Queue of prescriptions sorted by most recent activity
- Activity timeline per prescription
- Add events from prescription detail page
- Input validation on all fields
- Logging to `intake/workflow.log`

## Project Structure

```
intake/
├── manage.py
├── intake/          # Project settings
└── workflow/        # Main app (models, views, templates)
```
