from django.contrib.gis.db import models
from django.contrib import admin
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
    template_link = models.URLField(null=True, blank=True)
    termsofuse_link = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ["name"]
        db_table = "project"

    def __unicode__(self):
        return smart_str(self.name)

    def __str__(self):
        return self.__unicode__()

    def natural_key(self):
        return self.__unicode__()


class Organization(models.Model):
    """This table is useful to save info about organizations """
    name = models.CharField(max_length=255)
    shortname = models.CharField(max_length=25)
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
    shortname = models.CharField(max_length=25)
    organization = models.ForeignKey(Organization, on_delete=models.PROTECT)
    email = models.EmailField(null=True, blank=True)
    website = models.URLField(max_length=150, null=True, blank=True)
    image = models.ImageField(upload_to="logo/organizations/", null=True, blank=True)
    projects = models.ManyToManyField(Project, through="ResearchGroupProject")
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
    research_group = models.ManyToManyField(ResearchGroup)
    projects = models.ManyToManyField(Project)
    euromammals_username = models.TextField(max_length=500, null=True, blank=True, help_text="The username of the user in the Euromammals database")
    note = models.TextField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __unicode__(self):
        return smart_str(f"{self.first_name} {self.last_name}")

    def __str__(self):
        return self.__unicode__()

    def natural_key(self):
        return self.__unicode__()

    @property
    def is_datacurator(self):
        result = self.groups.filter(name__in="Datacurator, Superdatacurator").exists()
        if not result:
            result = self.is_superuser
        return result

    @admin.display(description="Research Groups")
    def research_group_list(self):
        return ", ".join([research_group.name for research_group in self.research_group.all()])

    @admin.display(description="Projects")
    def projects_list(self):
        return ", ".join([project.name for project in self.projects.all()])

    @admin.display(description="Organizations")
    def organizations_list(self):
        return ", ".join([research_group.organization.name for research_group in self.research_group.all()])


class ResearchGroupProject(models.Model):
    researchgroup = models.ForeignKey(ResearchGroup, on_delete=models.PROTECT)
    project = models.ForeignKey(Project, on_delete=models.PROTECT)
    year = models.IntegerField()
    contact_people = models.TextField()
    contact_user = models.ManyToManyField(User, null=True, blank=True)
    term_of_use = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ["researchgroup", "project"]

    def __str__(self):
        return f"{self.researchgroup} {self.project} {self.year}"

    def natural_key(self):
        return self.__unicode__()

    @admin.display(description="Contact People")
    def contact_user_list(self):
        return ", ".join([user.__str__() for user in self.contact_user.all()])

    @admin.display(description="Organization")
    def organization_name(self):
        return self.researchgroup.organization.name
