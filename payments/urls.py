# payments/urls.py

from django.urls import path
from .views import payment_home, clickpesa_webhook # MPYA: Import clickpesa_webhook

app_name = 'payments' # Ni vizuri kuwa na app_name kwa reverse lookups

urlpatterns = [
    path('', payment_home, name='payment_home'),
    path('webhooks/clickpesa/', clickpesa_webhook, name='clickpesa_webhook'), # MPYA: Ongeza webhook URL
]