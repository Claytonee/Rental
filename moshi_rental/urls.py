from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('rentals/', include('rentals.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('rentals.urls')),
    path('bookings/', include('bookings.urls')),
    path('payments/', include('payments.urls')),
#     path('reviews/', include('reviews.urls')),
#     path('api/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 





