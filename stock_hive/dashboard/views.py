from django.shortcuts import render
from datetime import date, timedelta
from .models import Product
import random

def index(request):
    total_sales = 54000
    total_revenue = 75000
    total_profit = 21000
    total_cost = 54000
    total_products = 868
    to_be_received = 120
    total_suppliers = 15
    total_categories = 8
    total_purchases = 35000
    returns = 2000

    labels = [(date.today() - timedelta(days=i)).strftime('%d %b') for i in range(5)][::-1]
    sales_data = [random.randint(1000, 5000) for _ in range(5)]
    purchases_data = [random.randint(500, 4000) for _ in range(5)]
    order_labels = labels
    ordered_data = [random.randint(20, 40) for _ in range(5)]
    delivered_data = [random.randint(15, 45) for _ in range(5)]

    cards = [
        {"label": "Sales", "value": total_sales, "icon": "bi-bar-chart", "color": "primary"},
        {"label": "Revenue", "value": total_revenue, "icon": "bi-graph-up", "color": "success"},
        {"label": "Profit", "value": total_profit, "icon": "bi-cash", "color": "warning"},
        {"label": "Cost", "value": total_cost, "icon": "bi-credit-card", "color": "danger"},
    ]

    context = {
        "cards": cards,
        "total_products": total_products,
        "to_be_received": to_be_received,
        "total_suppliers": total_suppliers,
        "total_categories": total_categories,
        "total_purchases": total_purchases,
        "returns": returns,
        "labels": labels,
        "sales_data": sales_data,
        "purchases_data": purchases_data,
        "order_labels": order_labels,
        "ordered_data": ordered_data,
        "delivered_data": delivered_data,
        "products": Product.objects.all()
    }

    return render(request, 'dashboard/index.html', context)



def inventory_view(request):
    return render(request, 'dashboard/inventory.html')

def orders_view(request):
    return render(request, 'dashboard/orders.html')

def reports_view(request):
    return render(request, 'dashboard/reports.html')

def settings_view(request):
    return render(request, 'dashboard/settings.html')
