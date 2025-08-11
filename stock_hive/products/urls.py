from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.product_list, name="list"),
    path("create/", views.product_create, name="create"),
    path("<int:pk>/edit/", views.product_update, name="edit"),
    path("<int:pk>/delete/", views.product_delete, name="delete"),
    path("<int:pk>/movements/", views.product_movements, name="movements"),
    path("<int:pk>/stock-in/", views.stock_in, name="stock_in"),
    path("<int:pk>/stock-out/", views.stock_out, name="stock_out"),
]
