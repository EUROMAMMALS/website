"""euromammals URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.views.i18n import JavaScriptCatalog
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
import website.views as wviews

js_info_dict = {
   'domain': 'django',
   'packages': None,
}

urlpatterns = [
    path("mammalsadmin/", admin.site.urls),
    #path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/password_change/',auth_views.PasswordChangeView.as_view(success_url="/"), name="password_change"),
    path('accounts/login/', auth_views.LoginView.as_view(), name="login"),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name="logout"),
    path("", wviews.homepage),
    path("contact/", wviews.contact_view),
    path("logos/", wviews.logos),
    path("events/", wviews.events),
    path("pagers/", wviews.pagers),
    path("pubs/", wviews.publications),
    path("education/", wviews.educational),
    path("euroboar/", wviews.project, {"projct": "EUROBOAR"}),
    path("eurolynx/", wviews.project, {"projct": "EUROLYNX"}),
    path("eurosmallmammals/", wviews.project, {"projct": "EUROSMALLMAMMALS"}),
    path("eurowildcat/", wviews.project, {"projct": "EUROWILDCAT"}),
    path("eurodeer/", wviews.project, {"projct": "EURODEER"}),
    path("eureddeer/", wviews.project, {"projct": "EUREDDEER"}),
    path("euroibex/", wviews.project, {"projct": "EUROIBEX"}),
    path("eurojackal/", wviews.project, {"projct": "EUROJACKAL"}),
    path("afrimove/", wviews.project, {"projct": "AfriMove"}),
    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n/', JavaScriptCatalog.as_view(), js_info_dict,
         name='javascript_catalog'),
] + static(settings.STATIC_URL,
           document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
