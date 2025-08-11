from django.contrib import messages
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from .forms import UserRegistrationForm

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data["role"]
            user = form.save()

            group_name = "admins" if role == "admin" else "employees"
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

            if role == "admin":
                user.is_staff = True
                user.save(update_fields=["is_staff"])

            messages.success(request, _("Account created successfully."))
            return redirect("accounts:login")
    else:
        form = UserRegistrationForm()

    return render(request, "register.html", {"form": form})
