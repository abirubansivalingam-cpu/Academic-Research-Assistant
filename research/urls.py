from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("search/", views.search_documents, name="search_documents"),
    path("evaluation/", views.evaluation_dashboard, name="evaluation_dashboard"),
    path("evaluation/run/", views.run_evaluation, name="run_evaluation"),
    path("evaluation/cases/<int:pk>/delete/", views.delete_evaluation_case, name="delete_evaluation_case"),
    path("evaluation/runs/<int:pk>/", views.evaluation_run_detail, name="evaluation_run_detail"),
    path("profile/", views.profile, name="profile"),
    path("documents/upload/", views.upload_document, name="upload_document"),
    path("documents/<int:pk>/", views.document_detail, name="document_detail"),
    path("documents/<int:pk>/extract/", views.extract_document_text, name="extract_document_text"),
    path("documents/<int:pk>/open/", views.open_document, name="open_document"),
    path("documents/<int:pk>/delete/", views.delete_document, name="delete_document"),
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
]
