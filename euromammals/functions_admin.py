import os
from django.forms import Form
from django.forms import FileField
from django.forms import CharField
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.staticfiles import finders

from .functions import read_csv

def csv_exists(table):
    """Check if CSV template exists otherwise return simple one"""
    result = finders.find(f"csv_template/{table}.csv")
    if result:
        return f"csv_template/{table}.csv"
    return "csv_template/simple.csv"


class FileImportForm(Form):
    file = FileField(label="CSV file")  # , help_text="CSV file containg the data")


class CsvImportForm(FileImportForm):
    separator = CharField(
        initial="|", label="Columns separator"
    )  # , help_text="Columns separator used in the CSV file")


class FilterProjectAdmin(admin.ModelAdmin):
    """General admin class to filter by projects"""

    list_filter = ["project"]

class CSVAdmin(admin.ModelAdmin):
    """General admin class to have capability to add CSV file"""

    change_list_template = "admin/import_csv.html"

    def _add_urls(self):
        return []

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("import-csv/", self.import_csv),
            path("download-csv/", self.get_csv),
        ]
        my_urls.extend(self._add_urls())
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["file"]
            separator = request.POST.get("separator")
            lines = csv_file.readlines()
            errors = read_csv(lines, self.model, separator)
            if len(errors) != 0:
                errs = ""
                for err in errors:
                    if "simpleerror" in err.keys():
                        errs += "{}\n".format(err.get("simpleerror"))
                    else:
                        errs += "line {id}: {er}\n".format(id=err["id"], er=", ".join(err["errors"]))
                self.message_user(
                    request, f"Your csv file has been NOT imported correctly:\n {errs}", level=messages.ERROR
                )
            else:
                self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/csv_form.html", payload)

    def get_csv(self, request):
        table = self.model._meta.db_table
        csv = csv_exists(table)
        csvpath = None
        for inpath in settings.STATICFILES_DIRS:
            tmpcsvpath = os.path.join(inpath, csv.lstrip("/"))
            if os.path.exists(tmpcsvpath):
                csvpath = tmpcsvpath
                break
        if not csvpath:
            return HttpResponseNotFound(f"CSV file for model {self.model} not found")
        with open(csvpath) as csvfile:
            data = csvfile.read()
        output = HttpResponse(data, content_type='text/csv')
        output['Content-Disposition'] = f'attachment; filename={table}.csv'
        return output
