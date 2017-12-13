from django.db import models
from users.models import OpenHumansMember


class Graph(models.Model):
    graph_type = models.CharField(max_length=200)
    graph_description = models.CharField(max_length=200)
    graph_data = models.TextField()
    open_humans_member = models.ForeignKey(OpenHumansMember,
                                           blank=True, null=True,
                                           on_delete=models.CASCADE)

    def __str__(self):
        return self.graph_type + ': ' + self.graph_description
