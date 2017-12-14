import requests

from .models import OpenHumansMember


def grant_access(request, oh_id):
    if oh_id is None:
        if request.user.is_authenticated:
            return request.user.openhumansmember.oh_id
    else:
        if (OpenHumansMember.objects.get(oh_id=oh_id).public or
           (request.user.is_authenticated and
           request.user.openhumansmember.oh_id == oh_id)):
            return oh_id
    return False


def get_file_url(oh_id):
    oh_member = OpenHumansMember.objects.get(oh_id=oh_id)
    token = oh_member.get_access_token()
    req = requests.get(
        'https://www.openhumans.org/api/direct-sharing/'
        'project/exchange-member/', params={'access_token': token})
    if req.status_code == 200 and 'data' in req.json():
        data = req.json()['data']
        # WARNING! This is assumes the first file encountered is what you want!
        if len(data) > 0:
            return data[0]['download_url']
    return None


def get_current_user(request):
    if request.user.is_authenticated:
        return request.user.openhumansmember.oh_id
    return None
