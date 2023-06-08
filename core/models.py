from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.encoding import smart_str
from django.utils.translation import gettext_lazy as _

# Create your models here.

class Country(models.Model):
    """Class for country info"""

    name = models.CharField(max_length=255)
    shortname = models.CharField(max_length=3)
    geom = models.MultiPolygonField(srid=4326)

    class Meta:
        ordering = ["name"]
        db_table = "country"

    def __unicode__(self):
        return smart_str(self.name)

    def __str__(self):
        return self.__unicode__()

    def natural_key(self):
        return self.__unicode__()


class Project(models.Model):
    """"""
    name = models.CharField(max_length=100)
    start_year = models.IntegerField()
    pager_status = models.URLField(null=True, blank=True)
    mailing_list = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        db_table = "projects"

    def __unicode__(self):
        return smart_str(self.name)

    def __str__(self):
        return self.__unicode__()

    def natural_key(self):
        return self.__unicode__()


class Organization(models.Model):
    """This table is useful to save info about organizations """
    name = models.CharField(max_length=255)
    shortname = models.CharField(max_length=15)
    address = models.CharField(max_length=250, null=True, blank=True)
    city = models.CharField(max_length=250, null=True, blank=True)
    country = models.ForeignKey(
        Country, on_delete=models.PROTECT, null=True, blank=True
    )
    email = models.EmailField(null=True, blank=True)
    website = models.URLField(max_length=150, null=True, blank=True)
    image = models.ImageField(upload_to="logo/organizations/", null=True, blank=True)
    geom = models.PointField(
        srid=4326,
        null=True,
        blank=True,
        help_text=_("The position of the organization"),
    )

    class Meta:
        ordering = ["name"]
        db_table = "organization"

    def __unicode__(self):
        if self.country:
            return smart_str(
                "{na} ({co})".format(na=self.name, co=self.country.shortname)
            )
        else:
            return smart_str("{na}".format(na=self.name))

    def __str__(self):
        return self.__unicode__()

    def natural_key(self):
        return self.__unicode__()


class ResearchGroup(models.Model):
    """"""
    name = models.CharField(max_length=255)
    shortname = models.CharField(max_length=15)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    year_joined = models.IntegerField()
    email = models.EmailField(null=True, blank=True)
    website = models.URLField(max_length=150, null=True, blank=True)
    image = models.ImageField(upload_to="logo/organizations/", null=True, blank=True)
    geom = models.PointField(
        srid=4326,
        null=True,
        blank=True,
        help_text=_("The position of the organization"),
    )

    class Meta:
        ordering = ["name"]
        db_table = "research_group"

    def __unicode__(self):
        if self.organization.shortname:
            return smart_str(
                "{na} ({co})".format(na=self.name, co=self.organization.shortname)
            )
        if self.organization.name:
            return smart_str(
                "{na} ({co})".format(na=self.name, co=self.organization.name)
            )
        else:
            return smart_str("{na}".format(na=self.name))

    def __str__(self):
        return self.__unicode__()

    def natural_key(self):
        return self.__unicode__()

class User(AbstractUser):
    """Extent the abstract user class"""

    bio = models.TextField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to="users/", null=True, blank=True)
    #TODO could a person be connected with more then one group?
    research_group = models.ForeignKey(
        ResearchGroup, on_delete=models.PROTECT, null=True, blank=True
    )
    projects = models.ManyToManyField(Project)
