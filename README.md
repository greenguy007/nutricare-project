# NutriCare Project

A comprehensive diet and nutrition management web application built with Django. NutriCare connects customers with dieticians to provide personalized diet plans, workout plans, and nutrition tracking.

## Features

### For Customers
- User registration and authentication
- BMI and BMR calculation
- Browse and join diet plans
- View and track custom diet plans
- Purchase workout plans
- Chat with dieticians
- Daily food logging and reports

### For Dieticians
- Professional registration with license verification
- Create and manage diet plans
- Upload diet plan PDFs
- Manage workout plans with videos
- Handle custom diet requests from customers
- Chat with customers

### For Admin
- Manage all users (customers, dieticians)
- View and manage diet plans and workout plans
- View feedbacks
- Dashboard with comprehensive statistics

## Technology Stack
- **Backend**: Django 4.x
- **Database**: SQLite (default)
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **AI**: Keras/TensorFlow chatbot for nutrition queries

## Installation

```bash
# Clone the repository
git clone https://github.com/greenguy007/nutricare-project.git

# Navigate to project directory
cd nutricare-project

# Install dependencies
pip install django

# Run migrations
python manage.py migrate

# Start the server
python manage.py runserver
```

## Project Structure
- `nutri_app/` - Main Django application
- `nutri_project/` - Django project settings
- `templates/` - HTML templates
- `static/` - CSS, JavaScript, and media files

## License
MIT License