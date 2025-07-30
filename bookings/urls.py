from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:item_id>/', views.create_booking, name='create_booking'),
    path('payment/<int:booking_id>/', views.payment, name='payment'),
    path('detail/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('list/', views.my_bookings, name='list'),
] 