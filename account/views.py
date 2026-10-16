from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect

from account.forms import UserForm, RegisterForm
from account.models import User


@login_required
def profile(request):
    return render(request, "account/profile.html")


@login_required
def profile_edit(request):
    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your details have been saved.")
            return redirect("blog:profile")
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
                return redirect("blog:index")

    else:
        form = RegisterForm()

    return render(request, "account/registration.html", {"form": form})