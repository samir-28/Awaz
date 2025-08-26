# Awaz

A web application designed to facilitate the lodging and management of complaints.

## Features

- **User Registration & Authentication**: Secure user sign-up and login functionality.
- **Complaint Submission**: Users can file complaints through an intuitive interface.
- **Complaint Dashboard**: View and manage submitted complaints.
- **Admin Panel**: Administrators can review, update, and resolve complaints.

## Tech Stack

- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python (Django)
- **Database**: SQLite (default), configurable

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/samir-28/Awaz.git
   cd Awaz
Create a virtual environment:

python -m venv venv
Activate the virtual environment:

Windows:


venv\Scripts\activate
macOS/Linux:

source venv/bin/activate
Install dependencies:


pip install -r requirements.txt
Apply database migrations:


python manage.py migrate
Run the development server:

python manage.py runserver
Access the application at http://127.0.0.1:8000/.

Usage
Navigate to the homepage to register or log in.

Once logged in, submit a complaint via the dashboard.

Administrators can manage complaints through the admin panel.
