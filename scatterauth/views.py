import random
import string
import json

from django.shortcuts import render, redirect, reverse
from django.urls.exceptions import NoReverseMatch
from django.contrib.auth import login, authenticate
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.http.request import split_domain_port

from scatterauth.forms import LoginForm, SignupForm
from scatterauth.settings import app_settings


def get_redirect_url(request):
    if request.GET.get('next'):
        return request.GET.get('next')
    elif request.POST.get('next'):
        return request.POST.get('next')
    elif settings.LOGIN_REDIRECT_URL:
        try:
            url = reverse(settings.LOGIN_REDIRECT_URL)
        except NoReverseMatch:
            url = settings.LOGIN_REDIRECT_URL
        return url



@require_http_methods(['POST'])
def login_api(request):
    form = LoginForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'success': False, 'error': json.loads(form.errors.as_json())})

    public_key = form.cleaned_data.get('public_key')
    nonce = form.cleaned_data.get('nonce')
    res = form.cleaned_data.get('res')

    if not nonce or not res or not public_key:
        return JsonResponse({'error': _(
            'Please pass message, signed message, and public key'),
            'success': False})

    user = authenticate(request, public_key=public_key, nonce=nonce, res=res)
    if user:
        login(request, user, 'scatterauth.backend.ScatterAuthBackend')
        return JsonResponse({'success': True, 'redirect_url': get_redirect_url(request)})
    else:
        error = _("Can't find a user for the provided signature with public key {public_key}").format(
                  public_key=public_key)
        return JsonResponse({'success': False, 'error': error})
        


@require_http_methods(['POST'])
def signup_api(request):
    if not app_settings.SCATTERAUTH_SIGNUP_ENABLED:
        return JsonResponse({'success': False, 'error': _("Sorry, signup's are currently disabled")})
    form = SignupForm(request.POST)
    if form.is_valid():
        user = form.save(commit=False)
        setattr(user, username, form.cleaned_data['publicKey'])
        user.save()
        login(request, user, 'scatterauth.backend.ScatterAuthBackend')
        return JsonResponse({'success': True, 'redirect_url': get_redirect_url(request)})
    else:
        return JsonResponse({'success': False, 'error': json.loads(form.errors.as_json())})


@require_http_methods(['GET', 'POST'])
def signup_view(request, template_name='scatterauth/signup.html'):
    '''
    1. Creates an instance of a SignupForm.
    2. Checks if the registration is enabled.
    3. If the registration is closed or form has errors, returns form with errors
    4. If the form is valid, saves the user without saving to DB
    5. Sets the user address from the form, saves it to DB
    6. Logins the user using scatterauth.backend.ScatterAuthBackend
    7. Redirects the user to LOGIN_REDIRECT_URL or 'next' in get or post params
    :param request: Django request
    :param template_name: Template to render
    :return: rendered template with form
    '''
    form = SignupForm()
    if not app_settings.SCATTERAUTH_SIGNUP_ENABLED:
        form.add_error(None, _("Sorry, signup's are currently disabled"))
    else:
        if request.method == 'POST':
            form = SignupForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                pubkey_field = app_settings.SCATTERAUTH_USER_PUBKEY_FIELD
                setattr(user, pubkey_field, form.cleaned_data[pubkey_field])
                user.save()
                print(pubkey_field)
                print(user.email)
                login(request, user, 'scatterauth.backend.ScatterAuthBackend')
                return redirect(get_redirect_url(request))
    return render(request, template_name, {'form': form})
