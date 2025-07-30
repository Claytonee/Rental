# accounts/adapter.py
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        """
        Inafanya redirect baada ya login
        """
        return reverse('rentals:dashboard')

    def get_signup_redirect_url(self, request):
        """
        Inafanya redirect baada ya signup
        """
        return reverse('rentals:dashboard')

    def save_user(self, request, user, form, commit=True):
        """
        Override hii ili kuhakikisha allauth inatumia CustomUser model
        na inahifadhi data vizuri.
        """
        user = super().save_user(request, user, form, commit=False)
        # Unaweza kuongeza fields zingine za CustomUser hapa kama zipo kwenye form ya signup
        # mfano:
        # user.phone_number = form.cleaned_data.get('phone_number')
        if commit:
            user.save()
        return user


