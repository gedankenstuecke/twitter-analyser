from django.db import models


class Graph(models.Model):
    graph_type = models.CharField(max_length=200)
    graph_description = models.CharField(max_length=200)
    graph_data = models.TextField()

    def __str__(self):
        return self.graph_type + ': ' + self.graph_description
