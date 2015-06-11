from django.db import models


class Place(models.Model):
    name = models.CharField(max_length=200)
    date_saved = models.DateTimeField()
