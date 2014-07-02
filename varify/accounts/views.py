from django.conf import settings
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.views import login
from django.views.decorators.cache import never_cache

from varify.accounts.utils import throttle_login, clear_throttled_login
from registration.forms import EmailAuthenticationForm


@never_cache
def throttled_login(request):
    "Displays the login form and handles the login action."
    # if the user is already logged-in, simply redirect them to the entry page
    if request.user.is_authenticated():
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    login_allowed = request.session.get('login_allowed', True)

    if request.method == 'POST':
        # If the session has already been flagged to not allow login attempts,
        # then simply redirect back to the login page.
        if not login_allowed:
            return HttpResponseRedirect(settings.LOGIN_URL)

        login_allowed = throttle_login(request)

    if login_allowed:
        response = login(request, authentication_form=EmailAuthenticationForm)
        # GHETTO: we know if the response is a redirect, the login
        # was successful, thus we can clear the throttled login counter
        if isinstance(response, HttpResponseRedirect):
            clear_throttled_login(request)
        return response

    return render_to_response('registration/login.html', {
        'login_not_allowed': not login_allowed
    }, context_instance=RequestContext(request))
