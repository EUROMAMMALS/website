from django.contrib import admin
from euromammals.functions_admin import FilterProjectAdmin

from .models import Pager

admin.site.register(Pager, FilterProjectAdmin)
