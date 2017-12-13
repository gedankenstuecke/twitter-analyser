from datetime import timedelta
import os

import arrow
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
import requests

OH_CLIENT_ID = os.getenv('OH_CLIENT_ID', '')
OH_CLIENT_SECRET = os.getenv('OH_CLIENT_SECRET', '')


def make_unique_username(base):
    """
    Ensure a unique username. Probably this never actually gets used.
    """
    try:
        User.objects.get(username=base)
    except User.DoesNotExist:
        return base
    n = 2
    while True:
        name = base + str(n)
        try:
            User.objects.get(username=name)
            n += 1
        except User.DoesNotExist:
            return name


class OpenHumansMember(models.Model):
    """
    Store OAuth2 data for Open Humans member.
    A User account is created for this Open Humans member.
    """
    user = models.OneToOneField(User)
    oh_id = models.CharField(max_length=16, primary_key=True, unique=True)
    access_token = models.CharField(max_length=256)
    refresh_token = models.CharField(max_length=256)
    token_expires = models.DateTimeField()
    public = models.BooleanField(default=False)

    @staticmethod
    def get_expiration(expires_in):
        return (arrow.now() + timedelta(seconds=expires_in)).format()

    @classmethod
    def create(cls, oh_id, access_token, refresh_token, expires_in):
        new_username = make_unique_username(
            base='{}_openhumans'.format(oh_id))
        new_user = User(username=new_username)
        new_user.save()
        oh_member = cls(
            user=new_user,
            oh_id=oh_id,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires=cls.get_expiration(expires_in))
        return oh_member

    def __str__(self):
        return "<OpenHumansMember(oh_id='{}')>".format(
            self.oh_id)

    def get_access_token(self):
        """
        Return access token. Refresh first if necessary.
        """
        # Also refresh if nearly expired (less than 60s remaining).
        delta = timedelta(seconds=60)
        if arrow.get(self.token_expires) - delta < arrow.now():
            self._refresh_tokens()
        return self.access_token

    def _refresh_tokens(self):
        """
        Refresh access token.
        """
        response = requests.post(
            'https://www.openhumans.org/oauth2/token/',
            data={
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token},
            auth=requests.auth.HTTPBasicAuth(
                settings.OH_CLIENT_ID, settings.OH_CLIENT_SECRET))
        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access_token']
            self.refresh_token = data['refresh_token']
            self.token_expires = self.get_expiration(data['expires_in'])
            self.save()
