import smtplib

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson
from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
from varify.support.forms import SupportForm

SUPPORT_EMAIL = getattr(settings, 'SUPPORT_EMAIL', None)


def send_support_mail(request, form):
    email = form.cleaned_data['email']
    subject = \
        '%s%s' % (settings.EMAIL_SUBJECT_PREFIX, form.cleaned_data['subject'])

    message = 'User-Agent: %s\n\n%s' % (
        request.META['HTTP_USER_AGENT'], form.cleaned_data['message'])

    send_mail(subject=subject, message=message,
              from_email=email, recipient_list=(SUPPORT_EMAIL,))


def ajax_form(request):
    if not request.is_ajax():
        raise Http404

    json = {'success': False}

    if request.method == 'POST':
        form = SupportForm(request.POST)
        if form.is_valid():
            try:
                send_support_mail(request, form)
                json['success'] = True
            except smtplib.SMTPException:
                pass

    return HttpResponse(simplejson.dumps(json), mimetype='application/json')


def form(request):
    error = False

    if request.method == 'POST':
        form = SupportForm(request.user, request.POST)
        if form.is_valid():
            try:
                send_support_mail(request, form)
                return HttpResponseRedirect(reverse('support-success'))
            except smtplib.SMTPException:
                error = True
    else:
        form = SupportForm(request.user)

    return render_to_response('support/form.html', {
        'form': form,
        'error': error,
    }, context_instance=RequestContext(request))


def success(request):
    return render_to_response('support/success.html',
                              context_instance=RequestContext(request))
