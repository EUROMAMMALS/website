from django import forms
from django.utils.translation import gettext_lazy as _
from core.models import Project

class ContactForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        projects = [(None, "----")]
        for proj in Project.objects.all():
            if proj.name != "EXTERNAL":
                projects.append((proj.id, proj.name))
        self.fields['project'].choices = projects

    contact_name = forms.CharField(
        required=True,
        help_text=_("Your name and surname")
    )
    from_email = forms.EmailField(
        required=True,
        help_text=_("Your e-mail address")
    )
    subject = forms.CharField(
        required=True,
        help_text=_("Subject")
    )
    project = forms.MultipleChoiceField(
        choices=(),
        help_text=_("If you are interested in a specific project please select the one"),
    )
    message = forms.CharField(
        widget=forms.Textarea,
        required=True,
        help_text=_("Message")
    )
