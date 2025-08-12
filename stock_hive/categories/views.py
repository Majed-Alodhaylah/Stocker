from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.translation import gettext as _
from .models import Category
from .forms import CategoryForm

@login_required
def category_list(request):
    seg = request.GET.get("segment", "")
    qs = Category.objects.all().order_by("name")
    if seg in {"grocery","ecom"}:
        qs = qs.filter(segment=seg)
    return render(request, "categories/list.html", {"items": qs, "segment": seg})

@login_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Category created."))
        return redirect("categories:list")
    return render(request, "categories/form.html", {"form": form, "title": _("Create Category")})

@login_required
def category_edit(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Category updated."))
        return redirect("categories:list")
    return render(request, "categories/form.html", {"form": form, "title": _("Edit Category")})

@login_required
def category_delete(request, pk):
    obj = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, _("Category deleted."))
        return redirect("categories:list")
    return render(request, "categories/confirm_delete.html", {"obj": obj})
