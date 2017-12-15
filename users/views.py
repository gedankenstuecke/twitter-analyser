import json
import logging
import os
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError

from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import requests

from tweet_display.helper import get_file_url
from tweet_display.tasks import import_data

from .models import OpenHumansMember
from .forms import UploadFileForm

# Open Humans settings
OH_BASE_URL = 'https://www.openhumans.org'
OH_API_BASE = OH_BASE_URL + '/api/direct-sharing'
OH_DELETE_FILES = OH_API_BASE + '/project/files/delete/'
OH_DIRECT_UPLOAD = OH_API_BASE + '/project/files/upload/direct/'
OH_DIRECT_UPLOAD_COMPLETE = OH_API_BASE + '/project/files/upload/complete/'

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


def delete_all_oh_files(oh_member):
    """
    Delete all current project files in Open Humans for this project member.
    """
    requests.post(
        OH_DELETE_FILES,
        params={'access_token': oh_member.get_access_token()},
        data={'project_member_id': oh_member.oh_id,
              'all_files': True})


def upload_file_to_oh(oh_member, filehandle, metadata):
    """
    This demonstrates using the Open Humans "large file" upload process.
    The small file upload process is simpler, but it can time out. This
    alternate approach is required for large files, and still appropriate
    for small files.
    This process is "direct to S3" using three steps: 1. get S3 target URL from
    Open Humans, 2. Perform the upload, 3. Notify Open Humans when complete.
    """
    # Remove any previous file - replace with this one.
    delete_all_oh_files(oh_member)

    # Get the S3 target from Open Humans.
    upload_url = '{}?access_token={}'.format(
        OH_DIRECT_UPLOAD, oh_member.get_access_token())
    req1 = requests.post(
        upload_url,
        data={'project_member_id': oh_member.oh_id,
              'filename': filehandle.name,
              'metadata': json.dumps(metadata)})
    if req1.status_code != 201:
        raise HTTPError(upload_url, req1.status_code,
                        'Bad response when starting file upload.')

    # Upload to S3 target.
    req2 = requests.put(url=req1.json()['url'], data=filehandle)
    if req2.status_code != 200:
        raise HTTPError(req1.json()['url'], req2.status_code,
                        'Bad response when uploading to target.')

    # Report completed upload to Open Humans.
    complete_url = ('{}?access_token={}'.format(
        OH_DIRECT_UPLOAD_COMPLETE, oh_member.get_access_token()))
    req3 = requests.post(
        complete_url,
        data={'project_member_id': oh_member.oh_id,
              'file_id': req1.json()['id']})
    if req3.status_code != 200:
        raise HTTPError(complete_url, req2.status_code,
                        'Bad response when completing upload.')

    # print('Upload done: "{}" for member {}.'.format(
    #    os.path.basename(filehandle.name), oh_member.oh_id))


def index(request):
    """
    Starting page for app.
    """
    context = {'client_id': settings.OH_CLIENT_ID,
               'oh_proj_page': settings.OH_ACTIVITY_PAGE,
               'redirect_uri': settings.OH_REDIRECT_URI}
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'users/index.html', context=context)


def complete(request):
    """
    Receive user from Open Humans. Store data, start data upload task.
    """
    logger.debug("Received user returning from Open Humans.")

    form = None

    if request.method == 'GET':
        # Exchange code for token.
        # This creates an OpenHumansMember and associated User account.
        code = request.GET.get('code', '')
        oh_member = oh_code_to_member(code=code)
        if oh_member:
            # Log in the user.
            user = oh_member.user
            login(request, user,
                  backend='django.contrib.auth.backends.ModelBackend')
        elif not request.user.is_authenticated:
            logger.debug('Invalid code exchange. User returned to start page.')
            return redirect('/')
        else:
            oh_member = request.user.openhumansmember

        if get_file_url(oh_member.oh_id) is not None:
            redirect('dashboard')

        form = UploadFileForm()
        context = {'oh_id': oh_member.oh_id,
                   'oh_proj_page': settings.OH_ACTIVITY_PAGE,
                   'form': form}
        return render(request, 'users/complete.html',
                      context=context)

    elif request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            metadata = {'tags': ['twitter', 'twitter-archive'],
                        'description': 'Twitter achive file.'}
            upload_file_to_oh(
                request.user.openhumansmember,
                request.FILES['file'],
                metadata)
        else:
            logger.debug('INVALID FORM')
        import_data.delay(request.user.openhumansmember.oh_id)
        return redirect('dashboard')


def public_data(request):
    public_user_list = OpenHumansMember.objects.filter(
                        public=True).order_by(
                        'oh_id')
    paginator = Paginator(public_user_list, 20)  # Show 20 contacts per page
    page = request.GET.get('page')
    try:
        public_users = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        public_users = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        public_users = paginator.page(paginator.num_pages)
    return render(request, 'users/public_data.html',
                  {'public_users': public_users,
                   'section': 'public_data'})


def dashboard(request):
    """
    Give options to delete account, make data public/private,
    reupload archive, trigger new parsing of archive.
    """
    if request.user.is_authenticated:
        oh_member = request.user.openhumansmember
        has_data = bool(get_file_url(oh_member.oh_id))
        context = {'client_id': settings.OH_CLIENT_ID,
                   'oh_proj_page': settings.OH_ACTIVITY_PAGE,
                   'oh_member': oh_member,
                   'has_data': has_data,
                   'section': 'home'}

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


def regenerate_graphs(request):
    if request.method == 'POST' and request.user.is_authenticated:
        import_data.delay(request.user.openhumansmember.oh_id)
    return redirect('dashboard')
