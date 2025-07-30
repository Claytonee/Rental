from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Avg
from django.core.paginator import Paginator
from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy # Kwa kutumia reverse_lazy kwa class-based views au redirect


# Import models and forms from your app
from .models import RentalItem, Category, Review
from .forms import RentalItemForm

# Import related models from other apps
from bookings.models import Booking


# --- Home Page Views ---
def home(request):
    """
    Renders the home page, displaying all categories and a selection of featured items.
    """
    categories = Category.objects.all()
    # Filter for available items and get the 8 most recently created
    featured_items = RentalItem.objects.filter(is_available=True).order_by('-created_at')[:8]

    # Define icons for categories (can be moved to a configuration file or database for scalability)
    category_icons = {
        'Electronics': 'laptop',
        'Tools': 'tools',
        'Sports': 'basketball-ball',
        'Party': 'glass-cheers',
        'Furniture': 'couch',
        'Other': 'box',
    }

    # Assign icons to category objects for template use
    for category in categories:
        category.icon = category_icons.get(category.name, 'box') # Default to 'box' if no specific icon

    context = {
        'categories': categories,
        'featured_items': featured_items,
    }
    return render(request, 'home.html', context)


# --- Item Listing and Detail Views ---
def item_list(request):
    """
    Displays a list of available rental items with search, category filtering,
    sorting, and pagination functionalities.
    """
    items = RentalItem.objects.filter(is_available=True)
    categories = Category.objects.all()

    # 1. Search functionality
    query = request.GET.get('q')
    if query:
        # Use Q objects for OR queries
        items = items.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct() # Use .distinct() to avoid duplicate results if an item matches both name and description

    # 2. Category filter
    category_id = request.GET.get('category')
    if category_id:
        try:
            items = items.filter(category_id=int(category_id))
        except ValueError:
            # Handle cases where category_id is not a valid integer
            messages.error(request, "Invalid category selected.")
            pass # Continue without filtering by category

    # 3. Sorting
    sort = request.GET.get('sort')
    if sort == 'price_asc':
        items = items.order_by('price_per_day')
    elif sort == 'price_desc':
        items = items.order_by('-price_per_day')
    elif sort == 'rating':
        # Annotate with average rating and order by it.
        # Ensure that items without reviews don't cause issues (e.g., they might appear first or last depending on DB)
        items = items.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating', '-created_at')
    elif sort == 'newest':
        items = items.order_by('-created_at')
    # Default sort if none specified or invalid
    else:
        items = items.order_by('-created_at') # Default to newest first

    # 4. Pagination
    paginator = Paginator(items, 12) # Show 12 items per page
    page_number = request.GET.get('page')
    items_on_page = paginator.get_page(page_number)

    context = {
        'items': items_on_page, # Pass the paginated items
        'categories': categories,
        'current_category': category_id,
        'current_sort': sort,
        'current_query': query,
    }
    return render(request, 'rentals/items.html', context)


def item_detail(request, pk):
    """
    Displays details of a single rental item, including its reviews.
    Allows authenticated users to submit or view their review.
    """
    item = get_object_or_404(RentalItem, pk=pk)
    # Select related user to avoid N+1 queries when accessing review.user in template
    reviews = item.reviews.select_related('user').order_by('-created_at')
    
    # Calculate average rating, default to 0 if no reviews
    # THIS LINE WAS CORRECTED: Removed () after average_rating
    avg_rating = int(item.average_rating or 0) 
    
    # THIS LINE WAS CORRECTED: Indentation fixed
    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    # Handle review submission/update directly on this page (if it's a POST request)
    if request.method == 'POST' and request.user.is_authenticated:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating and comment:
            # Validate rating to be an integer within a valid range (e.g., 1-5)
            try:
                rating = int(rating)
                if not (1 <= rating <= 5):
                    raise ValueError("Rating must be between 1 and 5.")
            except ValueError:
                messages.error(request, 'Invalid rating value.')
                return redirect('rentals:item_detail', pk=pk)

            if user_review:
                messages.error(request, 'You have already reviewed this item. To change it, please edit your existing review.')
            else:
                Review.objects.create(item=item, user=request.user, rating=rating, comment=comment)
                messages.success(request, 'Review submitted successfully!')
            return redirect('rentals:item_detail', pk=pk)
        else:
            messages.error(request, 'Please provide both rating and comment.')

    return render(request, 'rentals/detail.html', {
        'item': item,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'user_review': user_review
    })

@login_required
@require_POST # Ensure this view only accepts POST requests
def add_review(request, pk):
    """
    Handles adding or updating a review for a rental item via a POST request.
    This view is typically called from a form submission.
    """
    item = get_object_or_404(RentalItem, id=pk)
    rating = request.POST.get('rating')
    comment = request.POST.get('comment')

    if not (rating and comment):
        messages.error(request, 'Please provide both rating and comment.')
        return redirect('rentals:item_detail', pk=pk)

    try:
        rating = int(rating)
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5.")
    except ValueError:
        messages.error(request, 'Invalid rating value.')
        return redirect('rentals:item_detail', pk=pk)

    existing_review = Review.objects.filter(item=item, user=request.user).first()
    if existing_review:
        # Update existing review
        existing_review.rating = rating
        existing_review.comment = comment
        existing_review.save()
        messages.success(request, 'Review updated successfully!')
    else:
        # Create new review
        Review.objects.create(
            item=item,
            user=request.user,
            rating=rating,
            comment=comment
        )
        messages.success(request, 'Review submitted successfully!')

    return redirect('rentals:item_detail', pk=pk)


# --- Dashboard and Item Management Views for Users ---
@login_required
def dashboard(request):
    """
    Renders the user's dashboard (if you have one separate from user_items).
    This could show summary of rentals, bookings, etc.
    """
    return render(request, 'dashboard.html')

@login_required
def user_items(request):
    """
    Displays a list of rental items owned by the currently logged-in user,
    with an option to filter by category.
    """
    categories = Category.objects.all().order_by('name')
    selected_category = request.GET.get('category')
    items = RentalItem.objects.filter(owner=request.user)

    if selected_category:
        try:
            items = items.filter(category_id=int(selected_category))
        except ValueError:
            messages.error(request, "Invalid category selected.")
            pass

    return render(request, 'rentals/user_items.html', {
        'items': items,
        'categories': categories,
        'selected_category': selected_category
    })

@login_required
def add_item(request):
    """
    Handles the creation of a new rental item by the logged-in user.
    """
    if request.method == 'POST':
        form = RentalItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False) # Create item object but don't save to DB yet
            item.owner = request.user # Assign the logged-in user as the owner
            item.save() # Now save to DB
            messages.success(request, 'Item added successfully!')
            return redirect('rentals:user_items') # Redirect to user's items list
        else:
            # If form is not valid, pass the form with errors back to the template
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RentalItemForm() # Create an empty form for GET requests
    return render(request, 'rentals/add_item.html', {'form': form})

@login_required
def edit_item(request, item_id):
    """
    Allows the owner of an item or a superuser to edit an existing rental item.
    """
    item = get_object_or_404(RentalItem, id=item_id)
    # Check for ownership or superuser status
    if not (request.user.is_superuser or item.owner == request.user):
        messages.error(request, "You do not have permission to edit this item.")
        return redirect('rentals:user_items') # Redirect to a safe page

    if request.method == 'POST':
        form = RentalItemForm(request.POST, request.FILES, instance=item) # Populate form with instance data
        if form.is_valid():
            form.save() # Save changes to the item
            messages.success(request, 'Item updated successfully.')
            return redirect('rentals:user_items')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = RentalItemForm(instance=item) # Pre-fill form with existing item data for GET request
    return render(request, 'rentals/edit_item.html', {'form': form, 'item': item})

@login_required
@require_POST # This decorator ensures only POST requests are accepted
def delete_item(request, item_id):
    """
    Deletes a rental item. Only the owner or a superuser can perform this action.
    This function should only be accessed via a POST request (e.g., from a form).
    """
    item = get_object_or_404(RentalItem, id=item_id)
    # Check for authorization
    if not (request.user.is_superuser or item.owner == request.user):
        messages.error(request, "You do not have permission to delete this item.")
        return redirect('rentals:user_items')

    item.delete()
    messages.success(request, 'Item deleted successfully.')
    return redirect('rentals:user_items')

@login_required
def edit_review(request, pk):
    """
    Allows the user who created a review to edit it.
    """
    review = get_object_or_404(Review, pk=pk, user=request.user) # Ensure only owner can edit
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if not (rating and comment):
            messages.error(request, 'Please provide both rating and comment.')
            return render(request, 'rentals/edit_review.html', {'review': review})

        try:
            rating = int(rating)
            if not (1 <= rating <= 5):
                raise ValueError("Rating must be between 1 and 5.")
        except ValueError:
            messages.error(request, 'Invalid rating value.')
            return render(request, 'rentals/edit_review.html', {'review': review})

        review.rating = rating
        review.comment = comment
        review.save()
        messages.success(request, 'Review updated successfully!')
        return redirect('rentals:item_detail', pk=review.item.pk)
    # For GET request, display the form with current review data
    return render(request, 'rentals/edit_review.html', {'review': review})

@login_required
@require_POST # Ensures this is a POST request
def delete_review(request, pk):
    """
    Deletes a review. Only the user who created the review can delete it.
    """
    review = get_object_or_404(Review, pk=pk, user=request.user) # Ensure only owner can delete
    item_pk = review.item.pk # Get item PK before deleting review
    
    review.delete()
    messages.success(request, 'Review deleted successfully!')
    return redirect('rentals:item_detail', pk=item_pk)


# --- Admin Panel Views ---
# Decorator to ensure only superusers can access this view
@user_passes_test(lambda u: u.is_superuser)
def admin_panel(request):
    """
    Renders the main admin panel, showing all items, users, and bookings.
    Accessible only by superusers.
    """
    User = get_user_model()
    items = RentalItem.objects.all().order_by('-created_at')
    users = User.objects.all().order_by('-date_joined')
    bookings = Booking.objects.all().order_by('-start_date')
    booking_status_choices = Booking.STATUS_CHOICES

    context = {
        'items': items,
        'users': users,
        'bookings': bookings,
        'booking_status_choices': booking_status_choices,
    }
    return render(request, 'rentals/admin_panel.html', context)

@require_POST
@user_passes_test(lambda u: u.is_superuser) # Even if you check inside, decorator adds an extra layer
def change_booking_status(request, booking_id):
    """
    Allows a superuser to change the status of a booking.
    Accepts POST requests only.
    """
    # The user_passes_test decorator handles the permission check
    booking = get_object_or_404(Booking, id=booking_id)
    new_status = request.POST.get('status')

    # Validate the new status against defined choices
    valid_statuses = [choice[0] for choice in Booking.STATUS_CHOICES]
    if new_status in valid_statuses:
        booking.status = new_status
        booking.save()
        messages.success(request, f"Booking {booking.id} status updated to {booking.get_status_display()}.")
    else:
        messages.error(request, "Invalid status selected.")
    return redirect('rentals:admin_panel')

@require_POST
@user_passes_test(lambda u: u.is_superuser)
def toggle_admin(request, user_id):
    """
    Allows a superuser to promote/demote another user's admin status.
    Prevents a superuser from changing their own status.
    """
    # The user_passes_test decorator handles the permission check
    if request.user.id == user_id:
        messages.error(request, "You cannot change your own admin status.")
        return redirect('rentals:admin_panel')

    user_to_toggle = get_object_or_404(get_user_model(), id=user_id)
    
    # Toggle superuser and staff status
    user_to_toggle.is_superuser = not user_to_toggle.is_superuser
    user_to_toggle.is_staff = not user_to_toggle.is_staff # is_staff is often linked to superuser status for admin access
    user_to_toggle.save()
    messages.success(request, f"Admin status for {user_to_toggle.username} has been updated to {'Superuser' if user_to_toggle.is_superuser else 'Regular User'}.")
    return redirect('rentals:admin_panel')

@require_POST
@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, user_id):
    """
    Allows a superuser to delete another user's account.
    Prevents a superuser from deleting their own account.
    """
    # The user_passes_test decorator handles the permission check
    if request.user.id == user_id:
        messages.error(request, "You cannot delete your own account.")
        return redirect('rentals:admin_panel')

    user_to_delete = get_object_or_404(get_user_model(), id=user_id)
    user_to_delete.delete()
    messages.success(request, f"User {user_to_delete.username} has been deleted.")
    return redirect('rentals:admin_panel')


# --- Category Management Views ---
class CategoryForm(forms.ModelForm):
    """
    Form for creating and updating Category objects.
    (This usually goes in forms.py, but is kept here for context)
    """
    class Meta:
        model = Category
        fields = ['name', 'description']

@login_required
@user_passes_test(lambda u: u.is_superuser) # Only superusers should add categories in a typical setup
def add_category(request):
    """
    Allows a superuser to add a new category.
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully!')
            # Consider redirecting to a category list page or admin panel
            return redirect('rentals:admin_panel') # Or 'rentals:add_item' if that's preferred workflow
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CategoryForm()
    return render(request, 'rentals/add_category.html', {'form': form})

# Utility View
def go_to_admin_dashboard(request):
    """
    Redirects to Django's built-in admin site.
    """
    return redirect('/admin/')