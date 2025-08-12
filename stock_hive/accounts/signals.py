from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

@receiver(post_migrate)
def ensure_groups(sender, **kwargs):
    admins, _ = Group.objects.get_or_create(name="admins")
    employees, _ = Group.objects.get_or_create(name="employees")

    def add_perms(app_label, model, admin_perms=("add", "change", "delete", "view"),
                  employee_perms=("add", "change", "view")):
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model)
        except ContentType.DoesNotExist:
            return
        perms = Permission.objects.filter(content_type=ct, codename__in=[f"{p}_{model}" for p in admin_perms])
        admins.permissions.add(*perms)
        perms_emp = Permission.objects.filter(content_type=ct, codename__in=[f"{p}_{model}" for p in employee_perms])
        employees.permissions.add(*perms_emp)

    add_perms("products", "product",
              admin_perms=("add", "change", "delete", "view"),
              employee_perms=("add", "change", "view"))

    try:
        ct_cat = ContentType.objects.get(app_label="categories", model="category")
        admin_all = Permission.objects.filter(content_type=ct_cat)
        admins.permissions.add(*admin_all)
        view_only = Permission.objects.filter(content_type=ct_cat, codename="view_category")
        employees.permissions.add(*view_only)
    except ContentType.DoesNotExist:
        pass
