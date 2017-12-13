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
