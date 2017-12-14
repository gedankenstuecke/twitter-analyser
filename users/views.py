import logging
import os

from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect, render
import requests

from .models import OpenHumansMember
from django.contrib.auth.models import User
from tweet_display.tasks import import_data


# Open Humans settings
OH_BASE_URL = 'https://www.openhumans.org'

APP_BASE_URL = os.getenv('APP_BASE_URL', 'http://127.0.0.1:5000/users')
APP_PROJ_PAGE = 'https://www.openhumans.org/activity/twitter-archive-analyzer/'

# Set up logging.
logger = logging.getLogger(__name__)


def oh_get_member_data(token):
    """
    Exchange OAuth2 token for member data.
    """
    req = requests.get(
        '{}/api/direct-sharing/project/exchange-member/'.format(OH_BASE_URL),
        params={'access_token': token})
    if req.status_code == 200:
        return req.json()
    raise Exception('Status code {}'.format(req.status_code))
    return None


def oh_code_to_member(code):
    """
    Exchange code for token, use this to create and return OpenHumansMember.
    If a matching OpenHumansMember already exists in db, update and return it.
    """
    if settings.OH_CLIENT_SECRET and settings.OH_CLIENT_ID and code:
        data = {
            'grant_type': 'authorization_code',
            'redirect_uri': '{}/complete'.format(APP_BASE_URL),
            'code': code,
        }
        req = requests.post(
            '{}/oauth2/token/'.format(OH_BASE_URL),
            data=data,
            auth=requests.auth.HTTPBasicAuth(
                settings.OH_CLIENT_ID,
                settings.OH_CLIENT_SECRET
            ))
        data = req.json()
        if 'access_token' in data:
            oh_id = oh_get_member_data(
                data['access_token'])['project_member_id']
            try:
                oh_member = OpenHumansMember.objects.get(oh_id=oh_id)
                logger.debug('Member {} re-authorized.'.format(oh_id))
                oh_member.access_token = data['access_token']
                oh_member.refresh_token = data['refresh_token']
                oh_member.token_expires = OpenHumansMember.get_expiration(
                    data['expires_in'])
            except OpenHumansMember.DoesNotExist:
                oh_member = OpenHumansMember.create(
                    oh_id=oh_id,
                    access_token=data['access_token'],
                    refresh_token=data['refresh_token'],
                    expires_in=data['expires_in'])
                logger.debug('Member {} created.'.format(oh_id))
            oh_member.save()

            return oh_member
        elif 'error' in req.json():
            logger.debug('Error in token exchange: {}'.format(req.json()))
        else:
            logger.warning('Neither token nor error info in OH response!')
    else:
        logger.error('OH_CLIENT_SECRET or code are unavailable')
    return None


def index(request):
    """
    Starting page for app.
    """
    context = {'client_id': settings.OH_CLIENT_ID,
               'oh_proj_page': settings.OH_ACTIVITY_PAGE}
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'users/index.html', context=context)


def complete(request):
    """
    Receive user from Open Humans. Store data, start data upload task.
    """
    logger.debug("Received user returning from Open Humans.")

    # Exchange code for token.
    # This creates an OpenHumansMember and associated User account.
    code = request.GET.get('code', '')
    oh_member = oh_code_to_member(code=code)

    if oh_member:

        # Log in the user.
        # (You may want this if connecting user with another OAuth process.)
        user = oh_member.user
        login(request, user,
              backend='django.contrib.auth.backends.ModelBackend')

        # Initiate a data transfer task, then render 'complete.html'.
        # right now it defaults to just using the general twitter Archive
        # of @gedankenstuecke that's already on an URL
        # TODO: put in form for uploading zip archive instead.

        import_data.delay(oh_member.oh_id)
        context = {'oh_id': oh_member.oh_id,
                   'oh_proj_page': settings.OH_ACTIVITY_PAGE}
        return render(request, 'users/complete.html',
                      context=context)

    logger.debug('Invalid code exchange. User returned to starting page.')
    return redirect('/')


def dashboard(request):
    """
    Give options to delete account, make data public/private,
    reupload archive, trigger new parsing of archive.
    """
    if request.user.is_authenticated:
        oh_member = request.user.openhumansmember
        context = {'client_id': settings.OH_CLIENT_ID,
                   'oh_proj_page': settings.OH_ACTIVITY_PAGE,
                   'oh_member': oh_member}
        # TODO: check for whether person as already uploaded a zip archive
        # TODO: add form for uploading/replacing an archive!

        return render(request, 'users/dashboard.html', context=context)
    return redirect("/")


def delete_account(request):
    if request.user.is_authenticated:
        oh_member = request.user.openhumansmember
        oh_member.delete()
        request.user.delete()
    return redirect("/")


def access_switch(request):
    if request.user.is_authenticated:
        oh_member = request.user.openhumansmember
        if oh_member.public:
            oh_member.public = False
        else:
            oh_member.public = True
        oh_member.save()
    return redirect('dashboard')
