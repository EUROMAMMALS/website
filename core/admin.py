import os
from functools import reduce
from operator import or_
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import path
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q

# Register your models here.
from euromammals.functions_admin import CSVAdmin
from euromammals.functions_admin import CsvImportForm
from euromammals.functions_admin import csv_exists

from .models import Project
from .models import Organization
from .models import ResearchGroup
from .models import User
from .models import ResearchGroupProject

from .forms import CustomUserCreationForm
from .forms import CustomUserChangeForm
from .forms import UserImportForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_filter = ("is_staff", "is_superuser", "is_active", "groups", "projects")
    fieldsets = (
        (None, {"fields": ("email", "password", "first_name", "last_name")}),
        ("Personal info", {"fields": ["bio", "research_group", "projects", "image"]}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "first_name", "last_name", "email", "password1",
                "password2", "is_staff", "is_active", "is_superuser", "groups",
                "user_permissions", "bio", "research_group", "projects", "image"
            )}
        ),
    )
    search_fields = ("username", "email",)
    ordering = ("last_name", "first_name",)

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
            usermodel = get_user_model()
            csv_file = request.FILES["file"]
            separator = request.POST.get("separator")
            if request.POST.get("is_staff") == "on":
                is_staff = True
            else:
                is_staff = False
            if request.POST.get("is_superuser") == "on":
                is_superuser = True
            else:
                is_superuser = False
            lines = csv_file.readlines()
            header = lines[0].decode().strip().split(separator)
            emails = []
            errors = 0
            for line in lines[1:]:
                vals = line.decode().strip().split(separator)
                rg = vals[header.index("research_group")]
                username = vals[header.index("username")]
                regroup = None
                try:
                    regroup = ResearchGroup.objects.get(id=rg)
                except:
                    try:
                        regroup = ResearchGroup.objects.get(name=rg)
                    except:
                        try:
                            regroup = ResearchGroup.objects.get(shortname=rg)
                        except:
                            self.message_user(
                                request,
                                f"Research group with value {rg} not found. User {username} not upload",
                                level=messages.WARNING
                            )
                            errors += 1
                            continue
                user = usermodel.objects.create_user(
                    email = vals[header.index("email")],
                    username = username,
                    password = vals[header.index("password")],
                    is_staff = is_staff,
                    first_name = vals[header.index("first_name")],
                    last_name = vals[header.index("last_name")],
                    #bio = vals[header.index("bio")],
                    is_superuser = is_superuser
                )
                user.research_group.add(regroup)
                for proj in Project.objects.exclude(name__in=["EXTERNAL"]):
                    if vals[header.index(proj.name.lower())] == "TRUE":
                        user.projects.add(proj)
                user.save()
                mail_text = f"Dear {user.first_name} {user.last_name},\na new account on EUROMAMMALS website was created for you.\n"
                mail_text += f"Your username is {user.username} and password {vals[header.index('password')]}.\n"
                mail_text += f"You can login here https://euromammals.org/accounts/login/ \n"
                mail_text += f"Please change password as soon as possible at this link https://euromammals.org/accounts/password_change/ \n"
                mail_text += "Kind regards"
                try:
                    sentmail = send_mail("Registration to EUROMAMMALS website", mail_text, None, [user.email])
                except Exception as err:
                    self.message_user(
                        request,
                        f"Not able to send email to {user.username}: {err}",
                        level=messages.WARNING
                    )
                    errors += 1
                if sentmail == 0:
                    self.message_user(
                        request,
                        f"Not able to send email to {user.username}",
                        level=messages.WARNING
                    )
                    errors += 1
            if errors == 0:
                self.message_user(request, "Your csv file has been imported correctly")
            else:
                self.message_user(request, f"Your csv file has been imported but {errors} failed")
            return redirect("..")
        form = UserImportForm()
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

    def get_search_results(self, request, queryset, search_term):
        orig_queryset = queryset
        queryset, use_distinct = super(CSVAdmin, self).get_search_results(
                                               request, queryset, search_term)
        search_words = search_term.split()
        if search_words:
            q_objects = [Q(**{field + '__icontains': word})
                                for field in self.search_fields
                                for word in search_words]
            queryset |= self.model.objects.filter(reduce(or_, q_objects))

        queryset = queryset & orig_queryset
        return queryset, use_distinct


class ResearchGroupAdmin(CSVAdmin):
    search_fields = ("name", "organization__name")


class OrganizationAdmin(CSVAdmin):
    search_fields = ("name",)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Project, CSVAdmin)
admin.site.register(Organization, CSVAdmin)
admin.site.register(ResearchGroup, ResearchGroupAdmin)
admin.site.register(ResearchGroupProject, CSVAdmin)
