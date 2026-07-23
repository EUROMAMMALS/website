from django.urls import path

from . import views

urlpatterns = [
    path("metadata/<str:projct>/", views.metadata),
    path("metadata/<str:projct>/<int:area_id>/", views.metadata),
]
