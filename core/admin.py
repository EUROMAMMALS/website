from django.contrib import admin

# Register your models here.
from euromammals.functions_admin import CSVAdmin

from .models import Project
from .models import Organization
from .models import ResearchGroup
from .models import User

admin.site.register(User)
admin.site.register(Project, CSVAdmin)
admin.site.register(Organization, CSVAdmin)
admin.site.register(ResearchGroup, CSVAdmin)
