from datetime import date, timedelta

from django.db.models import Sum, F, Value, DecimalField, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.shortcuts import render

from products.models import Product
from inventory.models import StockMovement
from categories.models import Category
from suppliers.models import Supplier


def index(request):
    sales_qty = StockMovement.objects.filter(kind="OUT").aggregate(v=Sum("quantity"))["v"] or 0
    revenue = StockMovement.objects.filter(kind="OUT").aggregate(v=Sum(F("unit_price") * F("quantity")))["v"] or 0
    cost = StockMovement.objects.filter(kind="IN").aggregate(v=Sum(F("unit_price") * F("quantity")))["v"] or 0
    profit = (revenue or 0) - (cost or 0)

    total_products = Product.objects.count()
    total_suppliers = Supplier.objects.count()
    total_categories = Category.objects.count()
    inv_in_hand = Product.objects.aggregate(v=Sum("quantity"))["v"] or 0

    days = [date.today() - timedelta(days=i) for i in range(4, -1, -1)]
    labels = [d.strftime("%d %b") for d in days]
    sales_data, purchases_data, ordered_data, delivered_data = [], [], [], []

    for d in days:
        day_rev = StockMovement.objects.filter(kind="OUT", created_at__date=d).aggregate(
            v=Sum(F("unit_price") * F("quantity"))
        )["v"] or 0
        day_cost = StockMovement.objects.filter(kind="IN", created_at__date=d).aggregate(
            v=Sum(F("unit_price") * F("quantity"))
        )["v"] or 0
        day_out_qty = StockMovement.objects.filter(kind="OUT", created_at__date=d).aggregate(
            v=Sum("quantity")
        )["v"] or 0

        sales_data.append(int(day_rev))
        purchases_data.append(int(day_cost))
        ordered_data.append(int(day_out_qty))
        delivered_data.append(int(day_out_qty))

    cards = [
        {"label": "Sales",   "value": int(sales_qty),      "icon": "bi-bar-chart",   "color": "primary", "is_currency": False},
        {"label": "Revenue", "value": float(revenue or 0), "icon": "bi-graph-up",    "color": "success", "is_currency": True},
        {"label": "Profit",  "value": float(profit),       "icon": "bi-cash",        "color": "warning", "is_currency": True},
        {"label": "Cost",    "value": float(cost or 0),    "icon": "bi-credit-card", "color": "danger",  "is_currency": True},
    ]

    last_in_price_sq = StockMovement.objects.filter(
        product=OuterRef("pk"), kind="IN"
    ).order_by("-created_at").values("unit_price")[:1]

    products = (
        Product.objects.select_related("category")
        .prefetch_related("suppliers")
        .annotate(
            display_price=Coalesce(
                Subquery(last_in_price_sq, output_field=DecimalField(max_digits=12, decimal_places=2)),
                F("price"),
                Value(0, output_field=DecimalField(max_digits=12, decimal_places=2)),
            ),
            buying_price=F("price"),  
        )[:50]
    )

    context = {
        "cards": cards,
        "total_products": total_products,
        "inv_in_hand": int(inv_in_hand),
        "to_be_received": 0,
        "total_suppliers": total_suppliers,
        "total_categories": total_categories,
        "total_purchases": float(cost or 0),
        "total_cost": float(cost or 0),
        "returns": 0,
        "canceled_orders": 0,
        "labels": labels,
        "sales_data": sales_data,
        "purchases_data": purchases_data,
        "order_labels": labels,
        "ordered_data": ordered_data,
        "delivered_data": delivered_data,
        "products": products,
    }
    return render(request, "dashboard/index.html", context)


def inventory_view(request):
    return render(request, "dashboard/inventory.html")


def orders_view(request):
    return render(request, "dashboard/orders.html")


def reports_view(request):
    return render(request, "dashboard/reports.html")


def settings_view(request):
    return render(request, "dashboard/settings.html")


def home_public(request):
    return render(request, "home.html")
