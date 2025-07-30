from allauth.account.views import LoginView, SignupView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class CustomLoginView(LoginView):
    pass

@method_decorator(csrf_exempt, name='dispatch')
class CustomSignupView(SignupView):
    pass 