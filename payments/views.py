# payments/views.py

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.conf import settings
# Unaweza kuhitaji models kutoka app nyingine hapa, mfano:
# from bookings.models import Booking, Payment

def payment_home(request):
    """
    Simple home page for the payments app.
    """
    return HttpResponse('Payments Home')

@csrf_exempt # MUHIMU: Webhooks hazina CSRF token
@require_POST # Webhooks mara nyingi hutuma POST requests
def clickpesa_webhook(request):
    """
    Handles incoming webhook notifications from ClickPesa.
    This view should update the status of bookings/payments based on ClickPesa events.
    """
    try:
        payload = request.body.decode('utf-8')
        event = json.loads(payload)

        # --- VERY IMPORTANT: Implement Webhook Signature Verification ---
        # ClickPesa should provide a way to verify the webhook's authenticity
        # (e.g., a shared secret and a signature in the request headers).
        # This prevents malicious actors from sending fake webhook events.
        # Example (you need to adapt this based on ClickPesa's docs):
        # clickpesa_signature = request.headers.get('X-Clickpesa-Signature') # Check ClickPesa docs for header name
        # expected_signature = calculate_your_signature(payload, settings.CLICKPESA_WEBHOOK_SECRET)
        # if not hmac.compare_digest(clickpesa_signature, expected_signature):
        #     return HttpResponse(status=400, content="Invalid webhook signature")
        # -----------------------------------------------------------------

        event_type = event.get('event_type') # Check ClickPesa docs for actual event type field
        transaction_status = event.get('status') # Check ClickPesa docs for transaction status field
        reference_id = event.get('reference_id') # Your unique reference ID you sent to ClickPesa
        clickpesa_transaction_id = event.get('transaction_id') # ClickPesa's own transaction ID

        # Example: Handle a successful payment event
        if event_type == 'payment_status_update' and transaction_status == 'SUCCESS':
            # Find the corresponding booking/payment in your database
            # You might need to import Booking and Payment models here
            # from bookings.models import Booking, Payment
            try:
                # Assuming your Payment model has a field to store the reference_id
                payment_record = Payment.objects.get(transaction_id=reference_id)
                booking = payment_record.booking

                if payment_record.status != 'completed': # Avoid re-processing
                    payment_record.status = 'completed'
                    payment_record.transaction_id = clickpesa_transaction_id # Store ClickPesa's ID
                    payment_record.save()

                    booking.status = 'confirmed' # Update booking status
                    booking.save()
                    messages.success(request, f"Booking {booking.id} payment confirmed via ClickPesa webhook.")
                    print(f"Webhook: Payment for booking {booking.id} confirmed.")
                
            except Payment.DoesNotExist:
                print(f"Webhook Error: Payment record with reference_id {reference_id} not found.")
                return HttpResponse(status=404, content="Payment record not found")
            except Exception as e:
                print(f"Webhook Error processing success: {e}")
                return HttpResponse(status=500, content=f"Internal server error: {e}")

        elif event_type == 'payment_status_update' and transaction_status == 'FAILED':
            # Handle failed payments
            try:
                payment_record = Payment.objects.get(transaction_id=reference_id)
                if payment_record.status != 'failed':
                    payment_record.status = 'failed'
                    payment_record.save()
                    booking = payment_record.booking
                    booking.status = 'payment_failed' # Or 'cancelled'
                    booking.save()
                    print(f"Webhook: Payment for booking {booking.id} failed.")
            except Payment.DoesNotExist:
                print(f"Webhook Error: Payment record with reference_id {reference_id} not found for failure.")
            except Exception as e:
                print(f"Webhook Error processing failure: {e}")
                return HttpResponse(status=500, content=f"Internal server error: {e}")

        # Always return a 200 OK response to the webhook sender
        return JsonResponse({'status': 'success', 'message': 'Webhook received'})

    except json.JSONDecodeError:
        print("Webhook Error: Invalid JSON payload.")
        return HttpResponse(status=400, content="Invalid JSON payload")
    except Exception as e:
        print(f"Webhook Error: Unhandled exception: {e}")
        return HttpResponse(status=500, content=f"Unhandled webhook error: {e}")

# You might need to add these imports at the top of payments/views.py
# from bookings.models import Booking, Payment
# import hmac
# import hashlib