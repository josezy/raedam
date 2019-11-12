from django.contrib.auth import views
from django.shortcuts import resolve_url
from django.conf import settings


class AdminLoginView(views.LoginView):
    redirect_authenticated_user = True

    def get_success_url(self):
        url = self.get_redirect_url() or resolve_url(settings.LOGIN_REDIRECT_URL)

        if self.request.user.is_god:
            return url.replace('/admin/', '/server/', 1) or '/'

        return url.replace('/server/', '/admin/', 1) or '/'
