"""
Order models to be managed in django admin site.
"""


import csv
import datetime

from django.contrib import admin
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Order, OrderItem


def export_to_csv(modeladmin, request, queryset):
    """
    Custom admin action to download list of Orders as a CSV file
    """

    opts = modeladmin.model._meta
    content_disposition = "attachment; filename={opts.verbose_name}.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = content_disposition
    writer = csv.writer(response)

    fields = [
        field
        for field in opts.get_fields()
        if not field.many_to_many and not field.one_to_many
    ]
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime("%d/%m/%Y")
            data_row.append(value)
        writer.writerow(data_row)
    return response


export_to_csv.short_description = "Export to CSV"


class OrderItemInline(admin.TabularInline):
    """
    Include order_item model as inline
    """

    model = OrderItem
    raw_id_fields = ["product"]


def order_detail(obj):
    """
    Link to display the detail of each Order
    """
    url = reverse("orders:admin_order_detail", args=[obj.id])
    return mark_safe(f'<a href="{url}">View</a>')


def order_pdf(obj):
    """
    Link to pdf file of each order Order
    """
    url = reverse("orders:admin_order_pdf", args=[obj.id])
    return mark_safe(f'<a href="{url}">PDF</a>')


order_pdf.short_description = "Invoice"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Add Order model to admin site
    """

    list_display = [
        "id",
        "first_name",
        "last_name",
        "email",
        "address",
        "postal_code",
        "city",
        "paid",
        "created",
        "updated",
        order_detail,
        order_pdf,
    ]
    list_filter = ["paid", "created", "updated"]
    inlines = [OrderItemInline]
    actions = [export_to_csv]
