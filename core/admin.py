from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from euromammals.functions_admin import CSVAdmin

from .models import Project
from .models import Organization
from .models import ResearchGroup
from .models import User

admin.site.register(User, UserAdmin)
admin.site.register(Project, CSVAdmin)
admin.site.register(Organization, CSVAdmin)
admin.site.register(ResearchGroup, CSVAdmin)
