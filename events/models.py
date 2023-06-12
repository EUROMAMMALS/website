from django.db import models
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _

from core.models import Project
from core.models import User

# Create your models here.
EVENT_TYPE = (
    ('ME', _('Meeting')), ('CO', _('Conference')),
    ('SS', _('Summer school')), ('WO', _('Workshop')),
    ('TV', _('TV show')),
)

class Event(models.Model):
    """ Class for the events to show in the calendar """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    descr = models.TextField(null=True, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    typ = models.CharField(max_length=2, choices=EVENT_TYPE,
                           blank=True, null=True)
    venue = models.CharField(max_length=255, null=True, blank=True)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    as_participant = models.BooleanField(null=True, blank=True)
    # privato
    main_slide_link = models.URLField(null=True, blank=True)
    folder_slides_link = models.URLField(null=True, blank=True)
    report_link = models.URLField(null=True, blank=True)
    image_link = models.URLField(null=True, blank=True)
    registration_link = models.URLField(null=True, blank=True)
    registration_until = models.DateTimeField(null=True, blank=True)
    managers = models.ManyToManyField(User, blank=True)
    program_link = models.URLField(null=True, blank=True)
    # TODO think if it could be useful
    # logistic_link = models.URLField(null=True, blank=True)

    class Meta:
        db_table = 'event'
        ordering = ['-start']

    def __unicode__(self):
        outstr = f"{self.title}"
        if self.venue:
            outstr += f", {self.venue}"
        outstr += f", {self.start.date()}"
        if self.end:
            outstr += f" / {self.end.date()}"
        return smart_str(outstr)

    def __str__(self):
        return self.__unicode__()

    def natural_key(self):
        return self.__unicode__()
