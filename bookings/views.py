from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Booking, Payment
from rentals.models import RentalItem
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def create_booking(request, item_id):
    item = get_object_or_404(RentalItem, id=item_id)
    
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        # Validate dates
        if not start_date or not end_date:
            messages.error(request, 'Please select both start and end dates.')
            return redirect('rentals:item_detail', pk=item_id)
        
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d').date()
        
        if start_date < timezone.now().date():
            messages.error(request, 'Start date cannot be in the past.')
            return redirect('rentals:item_detail', pk=item_id)
        
        if end_date <= start_date:
            messages.error(request, 'End date must be after start date.')
            return redirect('rentals:item_detail', pk=item_id)
        
        # Check if item is available for these dates
        conflicting_bookings = Booking.objects.filter(
            item=item,
            status__in=['pending', 'confirmed'],
            start_date__lte=end_date,
            end_date__gte=start_date
        )
        
        if conflicting_bookings.exists():
            messages.error(request, 'Item is not available for the selected dates.')
            return redirect('rentals:item_detail', pk=item_id)
        
        # Create booking
        days = (end_date - start_date).days
        total_price = item.price_per_day * days
        
        booking = Booking.objects.create(
            user=request.user,
            item=item,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price
        )

        # Decrease item amount and update availability
        if item.amount > 1:
            item.amount -= 1
            item.save()
        else:
            item.amount = 0
            item.is_available = False
            item.save()
        
        # Create payment
        payment = Payment.objects.create(
            booking=booking,
            amount=total_price
        )
        
        # Create Stripe payment intent
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(total_price * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'booking_id': booking.id,
                    'payment_id': payment.id
                }
            )
            payment.stripe_payment_id = intent.id
            payment.save()
            
            return redirect('bookings:payment', booking_id=booking.id)
            
        except stripe.error.StripeError as e:
            messages.error(request, f'Payment error: {str(e)}')
            booking.delete()
            return redirect('rentals:item_detail', pk=item_id)
    
    return redirect('rentals:item_detail', pk=item_id)

@login_required
def payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    payment = booking.payment
    
    if payment.status == 'completed':
        messages.info(request, 'This booking has already been paid.')
        return redirect('bookings:booking_detail', booking_id=booking_id)
    
    context = {
        'booking': booking,
        'payment': payment,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'bookings/payment.html', context)

@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'bookings/detail.html', {'booking': booking})

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'bookings/list.html', {'bookings': bookings})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, 'This booking cannot be cancelled.')
        return redirect('bookings:booking_detail', booking_id=booking_id)
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        
        # Process refund if payment was made
        if booking.payment.status == 'completed':
            try:
                refund = stripe.Refund.create(
                    payment_intent=booking.payment.stripe_payment_id
                )
                booking.payment.status = 'refunded'
                booking.payment.save()
                messages.success(request, 'Booking cancelled and refund processed.')
            except stripe.error.StripeError as e:
                messages.error(request, f'Refund error: {str(e)}')
        else:
            messages.success(request, 'Booking cancelled successfully.')
        
        return redirect('bookings:my_bookings')
    
    return render(request, 'bookings/cancel_confirm.html', {'booking': booking}) 