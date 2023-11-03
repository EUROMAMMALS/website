from django.contrib import admin

from euromammals.functions_admin import CSVAdmin
from euromammals.functions_admin import FilterProjectAdmin

from .models import Event
from .models import EventExternal

class EventAdmin(CSVAdmin, FilterProjectAdmin):
    model = Event

admin.site.register(Event, EventAdmin)
admin.site.register(EventExternal, CSVAdmin)
