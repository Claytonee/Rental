# rentals/admin.py

from django.contrib import admin
from .models import Category, RentalItem, Review # Import models zako kutoka models.py


# Sajili models zako hapa ili zionekane kwenye Django Admin
admin.site.register(Category)
admin.site.register(RentalItem)
admin.site.register(Review)

# Unaweza kuongeza Admin classes kwa udhibiti zaidi baadaye (kama ulivyojifunza hapo awali)
# Kwa mfano, kwa Category:
# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'description', 'created_at')
#     search_fields = ('name',)