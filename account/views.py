from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from account.forms import UserForm, RegisterForm
from account.models import User, Lawyer


class ProfileView(LoginRequiredMixin, DetailView):
    """The logged-in user's own profile page.

    No pk/slug in the URL: the object is always request.user, so one user
    can never open another user's profile by changing the address.
    """

    model = User
    template_name = "account/profile.html"
    context_object_name = "profile_user"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lawyer"] = (
            Lawyer.objects
            .filter(user=self.object)
            .prefetch_related("specialty", "language")
            .first()
        )
        return context


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your details have been saved.")
            return redirect("account:profile")
    else:
        form = UserForm(instance=request.user)

    return render(request, "account/profile_edit.html", {"form": form})

def registration(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            first_name = form.cleaned_data.get("first_name")
            last_name = form.cleaned_data.get("last_name")
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            password_confirmation = form.cleaned_data.get("password_confirmation")
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username = username,
                        email = email,
                        password = password,
                        first_name=first_name,
                        last_name = last_name,
                    )

            except IntegrityError:
                form.add_error("username", "Username already exists.")
            else:
                login(request, user)
                messages.success(request, f"Successfully logged in, {username}!")
                return redirect("index")

    else:
        form = RegisterForm()

    return render(request, "account/registration.html", {"form": form})

class LawyerListView(ListView):
    model = Lawyer
    template_name = "account/lawyer_list.html"
    context_object_name = "lawyer_list"
    paginate_by = 20

    def get_queryset(self):
        return (
            Lawyer.objects
            .select_related("user")
            .prefetch_related("specialty", "language")
            .order_by("user__last_name", "user__first_name")
        )

class LawyerDetailView(DetailView):
    model = Lawyer
    template_name = "account/lawyer_detail.html"
    context_object_name = "lawyer"

    def get_queryset(self):
        return Lawyer.objects.select_related("user").prefetch_related("specialty", "language")
