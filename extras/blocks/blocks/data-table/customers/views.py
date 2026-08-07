import json
from decimal import Decimal
from urllib.parse import urlencode

from django.db.models import Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from labb.contrib.blocks import lm, render_page
from labb.signals import Dict, Int, Signals, Str

LbCustomer = lm("LbCustomer")
LbInvoice = lm("LbInvoice")
LbPlan = lm("LbPlan")

INDEX = "lb/data-table/customers/pages/index.html"
PAGE_SIZE = 8

# Sort key → ORM expression. The keys are what travel in the URL, so they stay
# short and stable even when the column moves or the annotation is renamed.
SORT_FIELDS = {
    "company": "company",
    "plan": "plan__price_monthly",
    "status": "status",
    "mrr": "mrr",
    "seats": "seats",
    "billed": "billed",
    "renews": "renews_on",
}
DEFAULT_SORT = "company"

STATUS_CHOICES = [
    ("active", "Active"),
    ("trial", "Trial"),
    ("past_due", "Past due"),
    ("churned", "Churned"),
]
STATUS_VALUES = {value for value, _ in STATUS_CHOICES}
STATUS_VARIANT = {
    "active": "success",
    "trial": "info",
    "past_due": "warning",
    "churned": "neutral",
}
HEALTH_VARIANT = {"good": "success", "watch": "warning", "at_risk": "error"}


# The shareable URL. Each field names the clean query key it restores from
# (query=), so one query string serves both a cold load and a Datastar request.
class QuerySignals(Signals):
    q = Str(path="filters.q", default="", query="q")
    status = Str(path="filters.status", default="", query="status")
    sort_field = Str(path="sort.field", default=DEFAULT_SORT, query="sort")
    sort_dir = Str(path="sort.dir", default="asc", query="dir")
    page = Int(default=1, min_value=1, query="page")


class UISignals(Signals):
    editing_pk = Int(path="ui.editingPk", default=0)
    selected = Dict(default_factory=dict)


def _query_signals(request):
    # Datastar requests carry the whole signal bag; a shared link carries only
    # the clean URL that replace-url wrote, which from_query reads back.
    s = QuerySignals(request) if request.signals else QuerySignals.from_query(request)
    if s.sort_field not in SORT_FIELDS:
        s.sort_field = DEFAULT_SORT
    if s.sort_dir not in ("asc", "desc"):
        s.sort_dir = "asc"
    if s.status not in STATUS_VALUES:
        s.status = ""
    return s


def _state_params(s, page):
    params = {}
    if s.q:
        params["q"] = s.q
    if s.status:
        params["status"] = s.status
    if s.sort_field != DEFAULT_SORT:
        params["sort"] = s.sort_field
    if s.sort_dir != "asc":
        params["dir"] = s.sort_dir
    if page > 1:
        params["page"] = page
    return params


def _url(name, s, page, **kwargs):
    base = reverse(f"block_data_table_customers:{name}", kwargs=kwargs)
    query = urlencode(_state_params(s, page))
    return f"{base}?{query}" if query else base


def _money(value):
    return f"{Decimal(value or 0):,.0f}"


def _next_dir(s, field):
    return "desc" if s.sort_field == field and s.sort_dir == "asc" else "asc"


def _filtered(s):
    qs = LbCustomer.objects.select_related("plan").annotate(
        billed=Coalesce(
            Sum("invoices__amount", filter=Q(invoices__status="paid")),
            Value(0),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ),
        overdue=Count("invoices", filter=Q(invoices__status="overdue"), distinct=True),
    )
    if s.q:
        qs = qs.filter(
            Q(company__icontains=s.q)
            | Q(contact_name__icontains=s.q)
            | Q(email__icontains=s.q)
            | Q(industry__icontains=s.q)
            | Q(country__icontains=s.q)
        )
    if s.status:
        qs = qs.filter(status=s.status)
    field = SORT_FIELDS[s.sort_field]
    return qs.order_by(f"-{field}" if s.sort_dir == "desc" else field, "pk")


def _summary(qs):
    totals = qs.aggregate(
        mrr=Coalesce(
            Sum("mrr"),
            Value(0),
            output_field=DecimalField(max_digits=12, decimal_places=2),
        ),
        seats=Coalesce(Sum("seats"), Value(0)),
    )
    return {
        "mrr": _money(totals["mrr"]),
        "seats": totals["seats"],
        "at_risk": qs.filter(health="at_risk").count(),
        "overdue": LbInvoice.objects.filter(customer__in=qs, status="overdue").count(),
    }


def _context(request, editing_pk=None):
    s = _query_signals(request)
    ui = UISignals(request)
    if editing_pk is not None:
        ui.editing_pk = editing_pk

    qs = _filtered(s)
    total = qs.count()
    total_pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = min(s.page, total_pages)
    s.page = page

    customers = list(qs[(page - 1) * PAGE_SIZE : page * PAGE_SIZE])
    for c in customers:
        c.initials = "".join(
            word[0] for word in c.company.split()[:2] if word[0].isalnum()
        ).upper()
        c.mrr_display = _money(c.mrr)
        c.billed_display = _money(c.billed)
        c.status_variant = STATUS_VARIANT.get(c.status, "neutral")
        c.health_variant = HEALTH_VARIANT.get(c.health, "neutral")

    editing = next((c for c in customers if c.pk == ui.editing_pk), None)

    return {
        "query_signals": s,
        "ui_signals": ui,
        "customers": customers,
        "editing_pk": ui.editing_pk,
        "update_url": _url("update", s, page, pk=editing.pk) if editing else "",
        "canonical_url": _url("index", s, page),
        "sort_field": s.sort_field,
        "sort_dir": s.sort_dir,
        "next_dir": {field: _next_dir(s, field) for field in SORT_FIELDS},
        "status_choices": STATUS_CHOICES,
        "searching": bool(s.q or s.status),
        "summary": _summary(qs),
        "plans": LbPlan.objects.all(),
        "page_pks": json.dumps([str(c.pk) for c in customers]),
        "first_index": (page - 1) * PAGE_SIZE + 1 if total else 0,
        "last_index": min(page * PAGE_SIZE, total),
        "total": total,
        "page": page,
        "total_pages": total_pages,
        "prev_page": page - 1,
        "next_page": page + 1,
    }


def _render(request, ctx):
    return render_page(request, INDEX, ctx, title=f"Customers ({ctx['total']})")


def index(request):
    return _render(request, _context(request))


def update(request, pk):
    customer = get_object_or_404(LbCustomer, pk=pk)
    if request.method == "POST":
        customer.contact_name = request.POST.get(
            "contact_name", customer.contact_name
        ).strip()
        customer.email = request.POST.get("email", customer.email).strip()
        customer.status = request.POST.get("status", customer.status)
        customer.seats = int(request.POST.get("seats") or customer.seats)
        customer.mrr = Decimal(request.POST.get("mrr") or customer.mrr)
        plan_pk = request.POST.get("plan")
        if plan_pk:
            customer.plan = LbPlan.objects.filter(pk=plan_pk).first()
        customer.save()
        if request.is_datastar:
            # A form POST carries form fields, not the signal bag — the query
            # string on the action URL is what keeps the view state alive.
            return _render(request, _context(request, editing_pk=0))
    return redirect("block_data_table_customers:index")


def delete(request, pk):
    if request.method in ("POST", "DELETE"):
        get_object_or_404(LbCustomer, pk=pk).delete()
        if request.is_datastar:
            return _render(request, _context(request))
    return redirect("block_data_table_customers:index")


def bulk_delete(request):
    if request.method == "POST":
        ui = UISignals(request)
        pks = [int(key) for key, on in ui.selected.items() if on]
        if pks:
            LbCustomer.objects.filter(pk__in=pks).delete()
        if request.is_datastar:
            ctx = _context(request)
            ctx["ui_signals"].selected = {}
            return _render(request, ctx)
    return redirect("block_data_table_customers:index")
