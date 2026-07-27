from django.db import models


# ---------------------------------------------------------------------------
# Arden — the demo product every block draws from.
# Revenue ops for growing teams: Workspace · Member · Customer · Invoice ·
# Plan · Event.
# ---------------------------------------------------------------------------

PLAN_SLUG_CHOICES = [
    ("starter", "Starter"),
    ("growth", "Growth"),
    ("scale", "Scale"),
]


class LbPlan(models.Model):
    """A subscription tier customers sit on."""

    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=20, unique=True, choices=PLAN_SLUG_CHOICES)
    tagline = models.CharField(max_length=200)
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=8, decimal_places=2)
    seats_included = models.PositiveSmallIntegerField(default=3)
    is_featured = models.BooleanField(default=False)
    features = models.JSONField(default=list, blank=True)

    class Meta:
        ordering = ["price_monthly"]

    def __str__(self):
        return self.name


class LbWorkspace(models.Model):
    """The account a team signs into. The demo runs inside one of these."""

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=60, unique=True)
    plan = models.ForeignKey(
        LbPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="workspaces"
    )
    region = models.CharField(max_length=40, default="eu-west-1")
    currency = models.CharField(max_length=3, default="USD")
    billing_email = models.EmailField(blank=True)
    trial_ends_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


MEMBER_ROLE_CHOICES = [
    ("owner", "Owner"),
    ("admin", "Admin"),
    ("member", "Member"),
    ("billing", "Billing"),
    ("viewer", "Viewer"),
]

MEMBER_STATUS_CHOICES = [
    ("active", "Active"),
    ("invited", "Invited"),
    ("suspended", "Suspended"),
]


class LbMember(models.Model):
    """A person on the workspace team — drives the settings/team surface."""

    workspace = models.ForeignKey(LbWorkspace, on_delete=models.CASCADE, related_name="members")
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    title = models.CharField(max_length=100, blank=True)
    role = models.CharField(max_length=20, choices=MEMBER_ROLE_CHOICES, default="member")
    status = models.CharField(max_length=20, choices=MEMBER_STATUS_CHOICES, default="active")
    two_factor = models.BooleanField(default=False)
    joined_on = models.DateField()
    last_active_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


CUSTOMER_STATUS_CHOICES = [
    ("active", "Active"),
    ("trial", "Trial"),
    ("past_due", "Past due"),
    ("churned", "Churned"),
]

CUSTOMER_HEALTH_CHOICES = [
    ("good", "Good"),
    ("watch", "Watch"),
    ("at_risk", "At risk"),
]


class LbCustomer(models.Model):
    """A company paying the workspace — the spine of the data table."""

    workspace = models.ForeignKey(LbWorkspace, on_delete=models.CASCADE, related_name="customers")
    company = models.CharField(max_length=120)
    contact_name = models.CharField(max_length=120)
    email = models.EmailField()
    plan = models.ForeignKey(
        LbPlan, on_delete=models.SET_NULL, null=True, blank=True, related_name="customers"
    )
    status = models.CharField(max_length=20, choices=CUSTOMER_STATUS_CHOICES, default="active")
    health = models.CharField(max_length=20, choices=CUSTOMER_HEALTH_CHOICES, default="good")
    mrr = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    seats = models.PositiveSmallIntegerField(default=1)
    industry = models.CharField(max_length=60, blank=True)
    country = models.CharField(max_length=60, blank=True)
    signed_up_on = models.DateField()
    renews_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["company"]

    def __str__(self):
        return self.company


INVOICE_STATUS_CHOICES = [
    ("paid", "Paid"),
    ("open", "Open"),
    ("overdue", "Overdue"),
    ("void", "Void"),
]


class LbInvoice(models.Model):
    """A billing run against a customer — the chartable revenue series."""

    customer = models.ForeignKey(LbCustomer, on_delete=models.CASCADE, related_name="invoices")
    number = models.CharField(max_length=30, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=20, choices=INVOICE_STATUS_CHOICES, default="paid")
    period = models.CharField(max_length=20, blank=True)
    issued_on = models.DateField()
    due_on = models.DateField()
    paid_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-issued_on", "-number"]

    def __str__(self):
        return self.number


EVENT_KIND_CHOICES = [
    ("signup", "Signup"),
    ("upgrade", "Upgrade"),
    ("downgrade", "Downgrade"),
    ("churn", "Churn"),
    ("payment", "Payment"),
    ("invite", "Invite"),
    ("seat_added", "Seat added"),
]


class LbEvent(models.Model):
    """Something that happened in the workspace — feeds activity feeds and charts."""

    workspace = models.ForeignKey(LbWorkspace, on_delete=models.CASCADE, related_name="events")
    customer = models.ForeignKey(
        LbCustomer, on_delete=models.CASCADE, null=True, blank=True, related_name="events"
    )
    kind = models.CharField(max_length=20, choices=EVENT_KIND_CHOICES)
    label = models.CharField(max_length=200)
    mrr_delta = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    occurred_at = models.DateTimeField()

    class Meta:
        ordering = ["-occurred_at"]

    def __str__(self):
        return self.label
