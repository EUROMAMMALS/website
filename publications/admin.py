from django.contrib import admin

from euromammals.functions_admin import CSVAdmin
from .views import BibtexAdmin

from .models import Publication
from .models import Journal
from .models import PublicationExternal

admin.site.register(Journal, CSVAdmin)
admin.site.register(Publication, BibtexAdmin)
admin.site.register(PublicationExternal, BibtexAdmin)
