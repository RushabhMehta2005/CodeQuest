from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import UserRegistrationForm, UserLoginForm
from .models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages


@login_required(login_url="/auth/login/")
def logout_view(request):
    logout(request)
    messages.success(request, "You are now logged out!")
    return redirect(reverse("Quest:home"))


def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "You are now successfully registered!")
            return redirect(reverse("custom_auth:login"))
    else:
        form = UserRegistrationForm()

    return render(
        request,
        "custom_auth/register.html",
        {
            "form": form,
        },
    )


def login_view(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You are now logged in!")
                return redirect(reverse("Quest:home"))
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(
        request,
        "custom_auth/login.html",
        {
            "form": form,
        },
    )


@login_required(login_url="/auth/login/")
def edit_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password is succesfully changed.")
            return redirect(reverse("custom_auth:login"))
        else:
            messages.error(request, "Invalid form.")
    else:
        form = PasswordChangeForm(request.user)
    return render(
        request,
        "custom_auth/edit.html",
        {
            "form": form,
        },
    )
