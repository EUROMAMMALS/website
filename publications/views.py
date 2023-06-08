import bibtexparser
from django.shortcuts import render
from django.urls import path
from django.shortcuts import redirect
from django.forms import ModelChoiceField

from euromammals.functions_admin import CSVAdmin
from euromammals.functions_admin import FileImportForm
from core.models import Project

from .models import Publication
from .models import Journal

class BibtexImportForm(FileImportForm):
    project = ModelChoiceField(queryset=Project.objects.all())


class BibtexAdmin(CSVAdmin):
    """Class to have capability to add Bibtex and CSV file"""

    change_list_template = "admin/import_bibtex.html"

    def _add_urls(self):
        my_urls = [
            path("import-bibtex/", self.import_bibtex),
        ]
        return my_urls

    def import_bibtex(self, request):
        if request.method == "POST":
            file = request.FILES["file"]
            proj = request.POST.get("project")
            bib_database = bibtexparser.load(file)

            for bib in bib_database.entries:
                journal_str = bib.journal
                try:
                    journal = Journal.objects.get(name=journal_str)
                except:
                    journal = Journal.objects.create(name=journal_str)
                Publication.objects.create(
                    title=bib.title,
                    year=bib.yearm,
                    journal=journal,
                    volume=bib.volume,
                    authors=bib.author,
                    abstract=bib.abstract,
                )
                self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = BibtexImportForm()
        payload = {"form": form}
        return render(request, "admin/bibtex_form.html", payload)