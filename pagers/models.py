from django.db import models
from django.utils.encoding import smart_str

from core.models import Project

class Pager(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    external_participant_link = models.URLField(null=True, blank=True)
    active = models.BooleanField(null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)

    class Meta:
        db_table = 'pager'
        ordering = ['title']

    def __unicode__(self):
        return smart_str(f"{self.title}")

    def __str__(self):
        return self.__unicode__()

    def natural_key(self):
        return self.__unicode__()