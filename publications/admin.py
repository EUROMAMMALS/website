from django.contrib import admin

from euromammals.functions_admin import CSVAdmin
from euromammals.functions_admin import FilterProjectAdmin

from .views import BibtexAdmin

from .models import Publication
from .models import Journal
from .models import PublicationExternal

class PublicationAdmin(BibtexAdmin, FilterProjectAdmin):
    model = Publication

admin.site.register(Journal, CSVAdmin)
admin.site.register(Publication, PublicationAdmin)
admin.site.register(PublicationExternal, BibtexAdmin)
