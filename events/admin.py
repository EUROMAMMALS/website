from django.contrib import admin

from euromammals.functions_admin import CSVAdmin

from .models import Event

admin.site.register(Event, CSVAdmin)