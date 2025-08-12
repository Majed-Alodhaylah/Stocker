from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from .forms import UserRegistrationForm

# هذه النماذج مطلوبة فقط لبناء صلاحيات الموظفين
from products.models import Product
from categories.models import Category
from suppliers.models import Supplier
from inventory.models import StockMovement


def ensure_groups():
    """
    ينشئ مجموعتي admins و employees إن لم تكن موجودة،
    ويعطي كل الصلاحيات للأدمن، وصلاحيات محدودة للموظفين.
    """
    admins, _ = Group.objects.get_or_create(name="admins")
    employees, _ = Group.objects.get_or_create(name="employees")

    # كل الصلاحيات للأدمن
    admins.permissions.set(Permission.objects.all())

    # صلاحيات محددة للموظفين
    perms = []

    def add_perms(model, codes):
        ct = ContentType.objects.get_for_model(model)
        for code in codes:
            perm = Permission.objects.filter(
                content_type=ct,
                codename=f"{code}_{model._meta.model_name}"
            ).first()
            if perm:
                perms.append(perm)

    add_perms(Product, ["view", "add", "change"])
    add_perms(StockMovement, ["view", "add", "change"])
    add_perms(Category, ["view"])
    add_perms(Supplier, ["view"])

    employees.permissions.set(perms)


@require_http_methods(["GET", "POST"])
def logout_view(request):
    """
    يدعم GET/POST لتفادي 405.
    تأكد أن زر الخروج في base.html يرسل POST:
      <form method="post" action="{% url 'accounts:logout' %}">{% csrf_token %}<button>...</button></form>
    """
    logout(request)
    messages.success(request, _("You have been logged out."))
    return redirect("home")


def register(request):
    """
    تسجيل مستخدم جديد مع إسناد الدور (أدمن/موظف) إلى المجموعة المناسبة.
    """
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            ensure_groups()
            user = form.save()
            role = form.cleaned_data.get("role")

            if role == "admin":
                group = Group.objects.get(name="admins")
                user.is_staff = True
                user.groups.add(group)
                user.save(update_fields=["is_staff"])
            else:
                group = Group.objects.get(name="employees")
                user.groups.add(group)

            messages.success(request, _("Account created. Welcome!"))
            return redirect("accounts:login")
    else:
        form = UserRegistrationForm()

    # base.html سيعرض واجهة التسجيل عند وجود show_register=True
    return render(request, "base.html", {"form": form, "show_register": True})
