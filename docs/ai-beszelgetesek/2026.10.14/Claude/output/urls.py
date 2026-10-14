from django.urls import path

from . import views

urlpatterns = [
    path("cases/new/", views.create_case, name="create_case"),
    path("cases/submitted/", views.case_submitted, name="case_submitted"),
]
