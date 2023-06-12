from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.
from euromammals.functions_admin import CSVAdmin

from .models import Project
from .models import Organization
from .models import ResearchGroup
from .models import User

from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    fieldsets = (
        (None, {"fields": ("email", "password", "first_name", "last_name")}),
        ("Personal info", {"fields": ["bio", "research_group", "projects", "image"]}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "is_superuser", "groups", "user_permissions",
                "bio", "research_group", "projects", "image"
            )}
        ),
    )
    search_fields = ("email",)
    ordering = ("last_name", "first_name",)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Project, CSVAdmin)
admin.site.register(Organization, CSVAdmin)
admin.site.register(ResearchGroup, CSVAdmin)
