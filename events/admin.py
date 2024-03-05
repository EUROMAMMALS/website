from django.contrib import admin

from euromammals.functions_admin import CSVAdmin

from .models import Event
from .models import EventExternal

class EventAdmin(CSVAdmin):
    model = Event
    list_filter = ["projects"]

admin.site.register(Event, EventAdmin)
admin.site.register(EventExternal, CSVAdmin)
