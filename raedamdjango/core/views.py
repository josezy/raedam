from django.urls import reverse
from django.shortcuts import redirect

from core.view_utils import BaseView


class Home(BaseView):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect(reverse('login'))

        if request.user.is_god:
            return redirect(reverse('admin:index'))

        return redirect(reverse('parking:spots'))
