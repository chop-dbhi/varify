from django.conf.urls.defaults import patterns, url
from django.conf import settings
from django.contrib.auth.views import login
from django.shortcuts import redirect
from django.views.generic import TemplateView


def login_redirect(request):
    if request.user.is_authenticated():
        return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        return login(request)


urlpatterns = patterns(
    '',
    url(r'^register/$', 'registration.views.register', name='register'),

    url(
        r'^register/complete/$',
        TemplateView.as_view(
            template_name='registration/registration_complete.html'),
        name='registration-complete'),

    url(r'^verify/(?P<activation_key>\w+)/$', 'registration.views.verify',
        name='verify-registration'),

    url(r'^moderate/(?P<activation_key>\w+)/$', 'registration.views.moderate',
        name='moderate-registration'),

    url(r'^moderate/$', 'registration.views.moderate_list',
        name='moderate-registration-list'),

    url(r'^login/$', login_redirect, name='login'),

    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login',
        name='logout'),
)
