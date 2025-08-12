from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Supplier
from .forms import SupplierForm

@login_required
def supplier_list(request):
    q = request.GET.get("q","").strip()
    qs = Supplier.objects.all()
    if q:
        qs = qs.filter(name__icontains=q)
    return render(request, "suppliers/list.html", {"items": qs, "q": q})

@login_required
def supplier_detail(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)
    return render(request, "suppliers/detail.html", {"obj": obj})

@login_required
def supplier_create(request):
    form = SupplierForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        obj = form.save()
        messages.success(request, "Supplier created.")
        return redirect("suppliers:detail", pk=obj.pk)
    return render(request, "suppliers/form.html", {"form": form, "title": "Add supplier"})

@login_required
def supplier_edit(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Supplier updated.")
        return redirect("suppliers:detail", pk=obj.pk)
    return render(request, "suppliers/form.html", {"form": form, "title": "Edit supplier"})

@login_required
def supplier_delete(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "Supplier deleted.")
        return redirect("suppliers:list")
    return render(request, "suppliers/confirm_delete.html", {"obj": obj})
