
#encoding=utf-8

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from dreamgadgetmail.models import Auth
from django.core.exceptions import ObjectDoesNotExist
import requests

@login_required
def index(request):
  return redirect('/')

@login_required
def mail_status(request):
  try:
    auth = Auth.objects.get(user=request.user)
  except ObjectDoesNotExist:
    auth = None

  # Auth phase to request the refresh token
  if not auth and request.GET.get('state', None) is not 'auth':
    oauth_auth_params = {
        'redirect_uri': settings.DREAMGADGETMAIL_REDIRECT_URI,
        'response_type': 'code',
        'client_id': settings.DREAMGADGETMAIL_CLIENT_ID,
        'approval_prompt': 'force',
        'scope': 'https://mail.google.com/mail/feed/atom/',
        'access_type': 'offline',
        'state': 'auth',
    }
    if request.GET.get('code', None) is None:
      return render(request, 'dreamgadgetmail/mail_status_request.html', {'auth_url': 'https://accounts.google.com/o/oauth2/auth?response_type=%(response_type)s&scope=%(scope)s&redirect_uri=%(redirect_uri)s&client_id=%(client_id)s&state=%(state)s&access_type=%(access_type)s' % oauth_auth_params})

  # Exchange authorization code for the refresh token
  if not auth:
    oauth_token_params = {
        'code': request.GET.get('code'),
        'redirect_uri': settings.DREAMGADGETMAIL_REDIRECT_URI,
        'client_id': settings.DREAMGADGETMAIL_CLIENT_ID,
        'scope': '',
        'client_secret': settings.DREAMGADGETMAIL_CLIENT_SECRET,
        'grant_type': 'authorization_code',
    }
    r = requests.post('https://accounts.google.com/o/oauth2/token', data=oauth_token_params)
    if 'error' in r.json:
      if r.json['error'] == 'invalid_grant':
        return redirect('mail_status')
      else:
        # Bad thing. Show error page?
        return render(request, 'dreamgadgetmail/mail_status_request.html')
    if 'access_token' not in r.json or 'refresh_token' not in r.json:
      # Bad thing. Show error page?
      return render(request, 'dreamgadgetmail/mail_status_request.html')
    access_token = r.json['access_token']
    refresh_token = r.json['refresh_token']
    Auth.objects.create(token=refresh_token, user=request.user)

  # If we already have the refresh token then attempt refreshing access token
  elif auth and auth.token is not None:
    oauth_refresh_params = {
        'refresh_token': auth.token,
        'client_id': settings.DREAMGADGETMAIL_CLIENT_ID,
        'client_secret': settings.DREAMGADGETMAIL_CLIENT_SECRET,
        'grant_type': 'refresh_token',
    }
    r = requests.post('https://accounts.google.com/o/oauth2/token', data=oauth_refresh_params)
    if 'error' in r.json:
      if r.json['error'] == 'invalid_grant':
        auth.delete()
        return redirect('mail_status')
      else:
        # Bad thing. Show error page?
        return render(request, 'dreamgadgetmail/mail_status_request.html')
    if 'access_token' not in r.json:
      # Bad thing. Show error page?
      return render(request, 'dreamgadgetmail/mail_status_request.html')
    access_token = r.json['access_token']

  # We have the access token so check mail count
  r = requests.get('https://mail.google.com/mail/feed/atom/', headers={'Authorization': 'OAuth ' + access_token})
  if '<fullcount>' in r.text:
    mail_count = int(r.text[r.text.find('<fullcount>') + 11:r.text.find('</fullcount>')])
  else:
    # This is bad too. Show error page?
    mail_count = 0

  if mail_count > 0:
    return render(request, 'dreamgadgetmail/mail_status_true.html', {'mail_count': mail_count})
  else:
    return render(request, 'dreamgadgetmail/mail_status_false.html')