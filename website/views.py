import os
import json
import glob
from datetime import date
from itertools import chain

from django.shortcuts import render
from django.conf import settings
from django.core.mail import send_mail

from core.models import Project
from events.models import Event
from publications.models import Publication
from pagers.models import Pager

from .forms import ContactForm


def homepage(request):
    """Function to return the home page"""
    today = date.today()
    myevents = Event.objects.filter(start__gt=today)[:6]
    pubs = Publication.objects.all()[:6]
    return render(request, template_name="home.html", context={"events": myevents, "pubs": pubs})


def contact_view(request):
    """Function for contact"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            #form.save()
            email_subject = {form.cleaned_data["subject"]}
            email_message = f"FROM: {form.cleaned_data['contact_name']}\nEMAIL: {form.cleaned_data['from_email']}\nMESSAGE: {form.cleaned_data['message']}"
            send_mail(email_subject, email_message, settings.CONTACT_EMAIL, settings.ADMIN_EMAIL)
            return render(request, 'email_sent.html')
    form = ContactForm()
    context = {'form': form}
    return render(request, 'contact.html', context)


def logos(request):
    """Function to return the logos"""
    suffix_dir = os.path.join("img", "logos")
    logodir = os.path.join(settings.STATIC_ROOT, suffix_dir)
    print(logodir)
    mylogos = []
    for root, dirs, files in os.walk(logodir):
        for fil in files:
            mylogos.append(os.path.join(suffix_dir, fil))
    print(logos)
    context = {"logos": mylogos}
    return render(request, 'logos.html', context)


def events(request):
    """Function to return the events"""
    myevents = Event.objects.all()
    return render(request, template_name="events.html", context={"events": myevents})


def publications(request):
    """Function to return the publications"""
    publis = Publication.objects.all()
    return render(request, template_name="pubs.html", context={"pubs": publis})


def educational(request):
    """Function to return the educational material"""
    return render(request, template_name="educational.html")


def project(request, projct):
    """Function to return project"""
    jsonpath = os.path.join(settings.STATIC_ROOT, "projects", f"{projct.lower()}.json")
    jsonfile = open(jsonpath)
    data = json.load(jsonfile)
    proj = Project.objects.get(name=projct)
    pubs = Publication.objects.filter(project=proj)
    events = Event.objects.filter(project=proj)
    return render(
        request,
        template_name="project.html",
        context={
            "data": data,
            "proj": projct.lower(),
            "pubs": pubs,
            "events": events,
        }
    )

def pagers(request):
    """Function to return pagers

    Args:
        request (obj): the request object
    """
    user_projs = request.user.projects.all()
    extproj = Project.objects.filter(name="EXTERNAL")
    all_projs = list(chain(user_projs, extproj))
    mypagers = Pager.objects.filter(project__in=all_projs)
    return render(request, template_name="pagers.html", context={"items": mypagers})
