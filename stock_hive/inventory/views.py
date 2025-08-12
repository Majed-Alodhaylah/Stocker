from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from .forms import ProductForm, StockAdjustForm
from .models import Product
from inventory.models import StockMovement


def _can_delete_products(user):
    return user.is_staff


@login_required
def product_list(request):
    q = request.GET.get("q", "").strip()
    qs = Product.objects.select_related("category").prefetch_related("suppliers").all()
    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(category__name__icontains=q) |
            Q(suppliers__name__icontains=q)
        ).distinct()
    paginator = Paginator(qs, 12)
    page = request.GET.get("page")
    items = paginator.get_page(page)
    return render(request, "products/list.html", {"items": items, "q": q})


@login_required
def product_detail(request, pk):
    obj = get_object_or_404(Product.objects.select_related("category").prefetch_related("suppliers"), pk=pk)
    return render(request, "products/detail.html", {"obj": obj})


@login_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        messages.success(request, _("Product created."))
        return redirect("products:detail", pk=obj.pk)
    return render(request, "products/form.html", {"form": form, "title": _("Create Product")})


@login_required
def product_edit(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Product updated."))
        return redirect("products:detail", pk=obj.pk)
    return render(request, "products/form.html", {"form": form, "title": _("Edit Product")})


@login_required
def product_delete(request, pk):
    if not _can_delete_products(request.user):
        messages.error(request, _("You don't have permission to delete products."))
        return redirect("products:detail", pk=pk)
    obj = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, _("Product deleted."))
        return redirect("products:list")
    return render(request, "products/confirm_delete.html", {"obj": obj})


@login_required
def product_adjust_stock(request, pk):
    obj = get_object_or_404(Product, pk=pk)
    form = StockAdjustForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        kind = form.cleaned_data["kind"]
        qty = form.cleaned_data["quantity"]
        unit_price = form.cleaned_data.get("unit_price") or 0
        note = form.cleaned_data.get("note", "")

        if kind == "IN":
            obj.quantity += qty
            obj.save(update_fields=["quantity"])
            StockMovement.objects.create(
                product=obj, kind="IN", quantity=qty, unit_price=unit_price,
                note=note, created_by=request.user
            )
            messages.success(request, _("Stock increased by %(q)s.") % {"q": qty})

        elif kind == "OUT":
            if qty > obj.quantity:
                messages.error(request, _("Cannot issue more than current stock."))
                return render(request, "products/adjust.html", {"form": form, "obj": obj})
            obj.quantity -= qty
            obj.save(update_fields=["quantity"])
            StockMovement.objects.create(
                product=obj, kind="OUT", quantity=qty, unit_price=unit_price,
                note=note, created_by=request.user
            )
            messages.success(request, _("Stock reduced by %(q)s.") % {"q": qty})

        else:  
            obj.quantity = qty
            obj.save(update_fields=["quantity"])
            StockMovement.objects.create(
                product=obj, kind="ADJ", quantity=qty, unit_price=0,
                note=note or "Adjusted to count", created_by=request.user
            )
            messages.success(request, _("Stock adjusted to %(q)s.") % {"q": qty})

        return redirect("products:detail", pk=obj.pk)

    return render(request, "products/adjust.html", {"form": form, "obj": obj})
