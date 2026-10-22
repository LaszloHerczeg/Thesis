from django.urls import path

from case import views

app_name = "case"
# TODO: fix urls
urlpatterns = [
    # ex:/case
    path("", views.CaseListView.as_view(), name="case_list"),
    # ex:/case/1
    path("<uuid:pk>/", views.CaseDetailView.as_view(), name="case_detail"),
    # ex:case/new
    path("new/", views.create_case, name="create_case"),
    # ex:case/submitted
    path("<uuid:pk>/results", views.classification_result, name="classification_result"),
    # ex:case/submitted
    path("<uuid:case_pk>/results/<int:classification_pk>", views.classification_result, name="classification_result"),

    path("<uuid:case_pk>/fail", views.classification_fail, name="classification_fail"),
    path("<uuid:case_pk>/not-suppoted", views.classification_not_supported, name="classification_not_supported"),
    path("<uuid:case_pk>/clarify", views.clarify, name="clarify"),
]