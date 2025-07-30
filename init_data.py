import os
import django
from django.utils import timezone
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moshi_rental.settings')
django.setup()

from django.contrib.auth import get_user_model
from rentals.models import Category, RentalItem
from django.core.files import File
from django.core.files.images import ImageFile

User = get_user_model()

def create_sample_data():
    # Create admin user
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@moshirental.com',
        password='admin123'
    )
    
    # Create regular user
    regular_user = User.objects.create_user(
        username='user',
        email='user@moshirental.com',
        password='user123',
        first_name='Regular',
        last_name='User'
    )
    
    # Create categories
    categories = [
        {
            'name': 'Electronics',
            'description': 'Electronic devices and gadgets',
            'icon': 'laptop'
        },
        {
            'name': 'Tools',
            'description': 'Tools and equipment',
            'icon': 'tools'
        },
        {
            'name': 'Sports',
            'description': 'Sports equipment and gear',
            'icon': 'basketball-ball'
        },
        {
            'name': 'Party',
            'description': 'Party supplies and equipment',
            'icon': 'glass-cheers'
        },
        {
            'name': 'Furniture',
            'description': 'Furniture and home items',
            'icon': 'couch'
        }
    ]
    
    created_categories = []
    for category_data in categories:
        category = Category.objects.create(
            name=category_data['name'],
            description=category_data['description']
        )
        created_categories.append(category)
    
    # Create rental items
    rental_items = [
        {
            'name': 'Professional Camera',
            'description': 'High-quality DSLR camera with multiple lenses',
            'category': 'Electronics',
            'price_per_day': 50.00,
            'owner': admin_user
        },
        {
            'name': 'Power Drill Set',
            'description': 'Complete power drill set with various attachments',
            'category': 'Tools',
            'price_per_day': 25.00,
            'owner': admin_user
        },
        {
            'name': 'Mountain Bike',
            'description': 'High-performance mountain bike for all terrains',
            'category': 'Sports',
            'price_per_day': 30.00,
            'owner': regular_user
        },
        {
            'name': 'Party Tent',
            'description': 'Large party tent with setup equipment',
            'category': 'Party',
            'price_per_day': 100.00,
            'owner': admin_user
        },
        {
            'name': 'Office Chair',
            'description': 'Ergonomic office chair with adjustable features',
            'category': 'Furniture',
            'price_per_day': 15.00,
            'owner': regular_user
        }
    ]
    
    for item_data in rental_items:
        category = next(c for c in created_categories if c.name == item_data['category'])
        RentalItem.objects.create(
            name=item_data['name'],
            description=item_data['description'],
            category=category,
            price_per_day=item_data['price_per_day'],
            owner=item_data['owner'],
            is_available=True
        )
    
    print("Sample data created successfully!")

if __name__ == "__main__":
    from bookings.models import Booking, Payment
    from rentals.models import RentalItem
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # Delete all bookings and payments
    Booking.objects.all().delete()
    Payment.objects.all().delete()
    RentalItem.objects.all().delete()

    # Delete all users except admin
    User.objects.exclude(username='admin').delete()

    # Ensure admin user exists and has correct permissions and password
    admin, created = User.objects.get_or_create(username='admin', defaults={
        'email': 'admin@moshirental.com',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True
    })
    admin.email = 'admin@moshirental.com'
    admin.is_staff = True
    admin.is_superuser = True
    admin.is_active = True
    admin.set_password('admin123')
    admin.save()
    print("All data deleted except for the admin user. Admin user is active, staff, superuser, and password reset.") 