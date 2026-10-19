from django.conf.urls.static import static
from django.urls import path, reverse_lazy
from account import views
from django.contrib.auth import views as auth_views
from django.conf import settings

app_name = "account"

urlpatterns = [
    # ex:/account/registration/
    path("registration/", views.registration, name="registration"),

    # ex:/account/login
    path("login/", auth_views.LoginView.as_view(template_name="account/login.html"), name="login"),

    # ex:/account/logout
    path("logout/",
         auth_views.LogoutView.as_view(
             template_name="account/logged_out.html",
         ), name="logout"),

    # ex:/account/profile
    path("profile/", views.profile, name="profile"),

    # ex:/account/profile-edit
    path("profile-edit/", views.profile_edit, name="profile_edit"),

    # ex:/account/password-reset/
    path("password-reset/",
         auth_views.PasswordResetView.as_view(
             template_name="account/password_reset_form.html",
             email_template_name="account/password_reset_email.html",
             success_url=reverse_lazy("account:password_reset_done"),
         ),
         name="password_reset"),

    # ex:/account/password-reset/done/
    path("password-reset/done/",
         auth_views.PasswordResetDoneView.as_view(
             template_name="account/password_reset_done.html",
         ),
         name="password_reset_done"),

    # ex:/account/reset/<uidb64>/<token>/
    path("reset/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(
             template_name="account/password_reset_confirm.html",
             success_url=reverse_lazy("account:password_reset_complete"),
         ),
         name="password_reset_confirm"),

    # ex:/account/reset/done
    path("reset/done/",
         auth_views.PasswordResetCompleteView.as_view(
             template_name="account/password_reset_complete.html",
         ),
         name="password_reset_complete"),

    # ex:/account/password-change
    path("password-change/",
         auth_views.PasswordChangeView.as_view(
             template_name="account/password_change_form.html",
             success_url=reverse_lazy("account:password_change_done"), ),
         name="password_change"),

    # ex:/account/password-change-done
    path("password-change/done/",
         auth_views.PasswordChangeDoneView.as_view(
             template_name="account/password_change_done.html",
         ),
         name="password_change_done"),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)