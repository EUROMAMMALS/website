from django.contrib import admin

from euromammals.functions_admin import CSVAdmin

from .models import Event
from .models import EventExternal

admin.site.register(Event, CSVAdmin)
admin.site.register(EventExternal, CSVAdmin)
