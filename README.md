<<<<<<< HEAD
# Moshi Rental System

A comprehensive rental management system built with Django and Bootstrap.

## Features

- User Authentication and Authorization
- Rental Item Management
- Booking and Order Processing
- Payment Integration (Stripe)
- Admin Dashboard
- Customer Dashboard
- Review and Rating System
- Search and Filtering
- REST API Endpoints

## Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up MySQL:
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE moshi_rental CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user (optional)
CREATE USER 'moshi_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON moshi_rental.* TO 'moshi_user'@'localhost';
FLUSH PRIVILEGES;
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
SECRET_KEY=your_secret_key
DEBUG=True
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key

# Database settings
DB_NAME=moshi_rental
DB_USER=root  # or your custom user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Initialize sample data:
```bash
python init_data.py
```

8. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

- `accounts/` - User authentication and profile management
- `rentals/` - Core rental functionality
- `bookings/` - Booking and order management
- `payments/` - Payment processing
- `reviews/` - Review and rating system
- `api/` - REST API endpoints

## Database Configuration

The system uses MySQL as its database. Make sure to:

1. Have MySQL server installed and running
2. Create the database with UTF-8 support
3. Configure the database connection in the `.env` file
4. Run migrations to create the database schema

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
=======
# Moshi Rental System

A comprehensive rental management system built with Django and Bootstrap.

## Features

- User Authentication and Authorization
- Rental Item Management
- Booking and Order Processing
- Payment Integration (Stripe)
- Admin Dashboard
- Customer Dashboard
- Review and Rating System
- Search and Filtering
- REST API Endpoints

## Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up MySQL:
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE moshi_rental CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user (optional)
CREATE USER 'moshi_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON moshi_rental.* TO 'moshi_user'@'localhost';
FLUSH PRIVILEGES;
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
SECRET_KEY=your_secret_key
DEBUG=True
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key

# Database settings
DB_NAME=moshi_rental
DB_USER=root  # or your custom user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

5. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Initialize sample data:
```bash
python init_data.py
```

8. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

- `accounts/` - User authentication and profile management
- `rentals/` - Core rental functionality
- `bookings/` - Booking and order management
- `payments/` - Payment processing
- `reviews/` - Review and rating system
- `api/` - REST API endpoints

## Database Configuration

The system uses MySQL as its database. Make sure to:

1. Have MySQL server installed and running
2. Create the database with UTF-8 support
3. Configure the database connection in the `.env` file
4. Run migrations to create the database schema

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
>>>>>>> 316df84 (Initial commit)
5. Create a Pull Request 