from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum, F
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product
from .forms import ProductForm, MovementForm
from inventory.models import StockMovement

try:
    from categories.models import Category
except Exception:
    Category = None


@login_required
def product_list(request):
    q     = request.GET.get('q', '').strip()
    cat   = request.GET.get('cat', '').strip()
    ptype = request.GET.get('type', '').strip()
    stat  = request.GET.get('status', '').strip()

    qs = Product.objects.all().select_related('category')

    if q:
        qs = qs.filter(
            Q(name__icontains=q) |
            Q(sku__icontains=q) |
            Q(barcode__icontains=q) |
            Q(brand__icontains=q)
        )
    if cat:
        qs = qs.filter(category_id=cat)
    if ptype:
        qs = qs.filter(product_type=ptype)
    if stat == "low":
        qs = qs.filter(quantity__lte=F('reorder_level'))

    qs = qs.order_by('name')

    paginator = Paginator(qs, 15)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'q': q, 'cat': cat, 'ptype': ptype, 'status': stat,
        'categories': (Category.objects.all() if Category else []),
    }
    return render(request, 'list.html', context)


@login_required
@permission_required("products.add_product", raise_exception=True)   
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created.")
            return redirect('products:list')
    else:
        form = ProductForm()
    return render(request, 'form.html', {'form': form, 'is_create': True})


@login_required
@permission_required("products.change_product", raise_exception=True)  
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated.")
            return redirect('products:list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'form.html', {'form': form, 'product': product, 'is_create': False})


@login_required
@permission_required("products.delete_product", raise_exception=True)  
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted.")
        return redirect('products:list')
    return render(request, 'confirm_delete.html', {'product': product})


@login_required
def product_movements(request, pk):
    product = get_object_or_404(Product, pk=pk)
    moves = StockMovement.objects.filter(product=product).order_by('-created_at')
    totals = moves.aggregate(
        total_in=Sum('quantity', filter=Q(kind='IN')),
        total_out=Sum('quantity', filter=Q(kind='OUT')),
    )
    return render(request, 'movements.html', {'product': product, 'moves': moves, 'totals': totals})


@login_required
@permission_required("inventory.add_stockmovement", raise_exception=True)  
def stock_in(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = MovementForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                mv = form.save(commit=False)
                mv.product = product
                mv.kind = 'IN'
                mv.created_by = request.user  
                mv.save()
                product.quantity = (product.quantity or 0) + mv.quantity
                product.save(update_fields=['quantity'])
            messages.success(request, "Stock IN recorded.")
            return redirect('products:movements', pk=product.pk)
    else:
        form = MovementForm()
    return render(request, 'stock_in.html', {'product': product, 'form': form})


@login_required
@permission_required("inventory.add_stockmovement", raise_exception=True) 
def stock_out(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = MovementForm(request.POST)
        if form.is_valid():
            mv_qty = form.cleaned_data.get('quantity')
            if mv_qty is None or mv_qty <= 0:
                form.add_error('quantity', "Invalid quantity.")
            elif (product.quantity or 0) < mv_qty:
                form.add_error('quantity', "Not enough stock.")
            else:
                with transaction.atomic():
                    mv = form.save(commit=False)
                    mv.product = product
                    mv.kind = 'OUT'
                    mv.created_by = request.user  
                    mv.save()
                    product.quantity = (product.quantity or 0) - mv_qty
                    product.save(update_fields=['quantity'])
                messages.success(request, "Stock OUT recorded.")
                return redirect('products:movements', pk=product.pk)
    else:
        form = MovementForm()
    return render(request, 'stock_out.html', {'product': product, 'form': form})
