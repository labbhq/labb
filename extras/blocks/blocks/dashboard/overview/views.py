import time
from collections import OrderedDict
from decimal import Decimal

from labb.contrib.blocks import lm, render_page
from labb.reactivity import SSEResponse, patch_signal
from labb.signals import Signals, Str

LbCustomer = lm("LbCustomer")
LbEvent = lm("LbEvent")
LbInvoice = lm("LbInvoice")
LbMember = lm("LbMember")
LbWorkspace = lm("LbWorkspace")

INDEX = "lb/dashboard/overview/pages/index.html"

MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

SERIES = OrderedDict(
    [
        ("billed", "Billed revenue"),
        ("movement", "MRR movement"),
    ]
)

STREAM_TICKS = 10
TICK_SECONDS = 0.25


class OverviewSignals(Signals):
    series = Str(path="series", default="billed")


def _money(value):
    return f"${Decimal(value or 0):,.0f}"


def _month_label(date):
    return f"{MONTHS[date.month - 1]} {date.year}"


def _month_axis(invoices):
    """Ordered month labels the whole page charts against."""
    seen = OrderedDict()
    for invoice in invoices:
        seen.setdefault((invoice.issued_on.year, invoice.issued_on.month), None)
    return [f"{MONTHS[m - 1]} {y}" for (y, m) in sorted(seen)]


def _billed_series(invoices, labels):
    totals = {label: Decimal(0) for label in labels}
    for invoice in invoices:
        if invoice.status == "paid":
            totals[_month_label(invoice.issued_on)] += invoice.amount
    return {
        "data": {
            "labels": [label.split(" ")[0] for label in labels],
            "datasets": [
                {
                    "label": "Collected",
                    "data": [float(totals[label]) for label in labels],
                    "backgroundColor": "primary",
                }
            ],
        }
    }


def _movement_series(events, labels):
    won = {label: Decimal(0) for label in labels}
    lost = {label: Decimal(0) for label in labels}
    for event in events:
        label = _month_label(event.occurred_at)
        if label not in won:
            continue
        if event.mrr_delta > 0:
            won[label] += event.mrr_delta
        else:
            lost[label] += -event.mrr_delta
    return {
        "data": {
            "labels": [label.split(" ")[0] for label in labels],
            "datasets": [
                {
                    "label": "New and expansion",
                    "data": [float(won[label]) for label in labels],
                    "backgroundColor": "success",
                },
                {
                    "label": "Churned and contracted",
                    "data": [float(-lost[label]) for label in labels],
                    "backgroundColor": "error",
                },
            ],
        }
    }


def _cohort_series(customers):
    cohorts = OrderedDict()
    for customer in sorted(customers, key=lambda c: c.signed_up_on):
        year = customer.signed_up_on.year
        total, kept = cohorts.get(year, (0, 0))
        cohorts[year] = (total + 1, kept + (0 if customer.status == "churned" else 1))
    return {
        "data": {
            "labels": [str(year) for year in cohorts],
            "datasets": [
                {
                    "label": "Still paying (%)",
                    "data": [
                        round(kept / total * 100, 1) for total, kept in cohorts.values()
                    ],
                    "backgroundColor": "accent",
                }
            ],
        }
    }


def _plan_series(customers):
    mix = OrderedDict()
    for customer in customers:
        if customer.status == "churned" or customer.plan is None:
            continue
        mix[customer.plan.name] = mix.get(customer.plan.name, Decimal(0)) + customer.mrr
    return {
        "data": {
            "labels": list(mix),
            "datasets": [{"label": "MRR", "data": [float(v) for v in mix.values()]}],
        }
    }


def _context(request):
    signals = OverviewSignals(request)
    series = signals.series if signals.series in SERIES else "billed"

    workspace = LbWorkspace.objects.select_related("plan").first()
    customers = list(LbCustomer.objects.select_related("plan").all())
    invoices = list(LbInvoice.objects.all())
    events = list(LbEvent.objects.select_related("customer").all())

    labels = _month_axis(invoices)
    active = [c for c in customers if c.status == "active"]
    churned = [c for c in customers if c.status == "churned"]
    mrr = sum((c.mrr for c in active), Decimal(0))

    latest = labels[-1] if labels else ""
    net_new = sum(
        (e.mrr_delta for e in events if _month_label(e.occurred_at) == latest),
        Decimal(0),
    )

    at_risk = sorted(
        (
            c
            for c in customers
            if c.health in ("at_risk", "watch") and c.status != "churned"
        ),
        key=lambda c: (0 if c.health == "at_risk" else 1, -c.mrr),
    )[:5]
    at_risk_mrr = sum((c.mrr for c in at_risk), Decimal(0))
    for customer in at_risk:
        customer.mrr_display = _money(customer.mrr)

    movements = [e for e in events if e.mrr_delta != 0][:6]
    for event in movements:
        event.delta_display = _money(abs(event.mrr_delta))

    return {
        "signals": signals,
        "series": series,
        "series_choices": SERIES,
        "workspace": workspace,
        "seats": LbMember.objects.count(),
        "period": latest,
        "mrr": _money(mrr),
        "net_new": _money(abs(net_new)),
        "net_new_up": net_new >= 0,
        "arr": _money(mrr * 12),
        "active_count": len(active),
        "customer_count": len(customers),
        "churn_rate": round(len(churned) / len(customers) * 100, 1) if customers else 0,
        "churned_count": len(churned),
        "at_risk": at_risk,
        "at_risk_mrr": _money(at_risk_mrr),
        "movements": movements,
        "revenue_chart": (
            _billed_series(invoices, labels)
            if series == "billed"
            else _movement_series(events, labels)
        ),
        "cohort_chart": _cohort_series(customers),
        "plan_chart": _plan_series(customers),
    }


def index(request):
    return render_page(request, INDEX, _context(request), title="Revenue overview")


def cash_stream(request):
    """Settle today's open invoices one by one, live, onto the collected-today card.

    Real rows, not a random walk: each tick banks the next open invoice, so the
    number the card lands on is the number the table would show.
    """
    invoices = list(
        LbInvoice.objects.filter(status="open").order_by("due_on")[:STREAM_TICKS]
    )

    def generate():
        collected = Decimal(0)
        for count, invoice in enumerate(invoices, start=1):
            collected += invoice.amount
            yield patch_signal(
                {"collected": {"total": _money(collected), "count": count}}
            )
            time.sleep(TICK_SECONDS)

    return SSEResponse(generate())
