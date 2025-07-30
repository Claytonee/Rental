from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    path('', views.home, name='home'),
    path('items/', views.item_list, name='item_list'),
    path('items/<int:pk>/', views.item_detail, name='item_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-item/', views.add_item, name='add_item'),
    path('my-items/', views.user_items, name='user_items'),
    path('add-category/', views.add_category, name='add_category'),
    path('items/<int:pk>/add-review/', views.add_review, name='add_review'),
    path('reviews/<int:pk>/edit/', views.edit_review, name='edit_review'),
    path('reviews/<int:pk>/delete/', views.delete_review, name='delete_review'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('items/<int:item_id>/delete/', views.delete_item, name='delete_item'),
    path('admin-panel/users/<int:user_id>/toggle-admin/', views.toggle_admin, name='toggle_admin'),
    path('admin-panel/users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('items/<int:item_id>/edit/', views.edit_item, name='edit_item'),
    path('bookings/<int:booking_id>/change-status/', views.change_booking_status, name='change_booking_status'),
    path('go-admin/', views.go_to_admin_dashboard, name='go_to_admin'),
] 