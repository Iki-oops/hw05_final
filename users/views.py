from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import UserCreation


class SignUp(CreateView):
    form_class = UserCreation
    success_url = reverse_lazy('signup')
    template_name = 'signup.html'
