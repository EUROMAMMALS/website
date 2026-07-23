from django.urls import path

from . import views

urlpatterns = [
    path("metadata/<str:projct>/", views.metadata),
]
