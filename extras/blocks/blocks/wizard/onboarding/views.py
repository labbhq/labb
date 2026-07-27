import datetime
import re

from django.utils import timezone

from labb.contrib.blocks import lm, render_page
from labb.signals import Int, Signals, Str

LbMember = lm("LbMember")
LbPlan = lm("LbPlan")
LbWorkspace = lm("LbWorkspace")

INDEX = "lb/wizard/onboarding/pages/index.html"
TITLE = "Set up your Arden workspace"

TOTAL_STEPS = 3
TRIAL_DAYS = 14
INVITE_SLOTS = (1, 2, 3)
INVITE_PLACEHOLDERS = [
    "jonah@kiteandbell.com",
    "rosa@kiteandbell.com",
    "finance@kiteandbell.com",
]

REGIONS = [
    ("eu-west-1", "EU West · Ireland"),
    ("us-east-1", "US East · Virginia"),
    ("ap-south-1", "Asia Pacific · Mumbai"),
]

ROLES = [
    ("member", "Member — can see revenue, cannot change billing"),
    ("admin", "Admin — can invite people and change billing"),
    ("viewer", "Viewer — read-only access to dashboards"),
]

PLAN_SLUGS = ["starter", "growth", "scale"]

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class OnboardingSignals(Signals):
    """Every answer the wizard collects lives here, and nowhere else.

    The step counter sits alongside the answers, so one signal bag carries the
    whole wizard: moving between steps is a normal request that ships the bag,
    which is why going back never loses what was typed.
    """

    step           = Int(default=1, min_value=1, max_value=TOTAL_STEPS)
    workspace_name = Str(path="form.workspace_name", default="")
    workspace_slug = Str(path="form.workspace_slug", default="")
    region         = Str(path="form.region",      default="eu-west-1", choices=[r[0] for r in REGIONS])
    invite_1       = Str(path="form.invite_1",    default="")
    invite_2       = Str(path="form.invite_2",    default="")
    invite_3       = Str(path="form.invite_3",    default="")
    invite_role    = Str(path="form.invite_role", default="member", choices=[r[0] for r in ROLES])
    plan           = Str(path="form.plan",        default="", choices=PLAN_SLUGS)


def _invites(s):
    """The invite fields that were actually filled in, in slot order."""
    raw = [getattr(s, f"invite_{i}") for i in INVITE_SLOTS]
    return [e.strip() for e in raw if e.strip()]


def _initials(email):
    local = email.split("@")[0]
    parts = [p for p in re.split(r"[._-]+", local) if p]
    letters = "".join(p[0] for p in parts[:2]) or local[:1]
    return letters.upper()


def _display_name(email):
    local = email.split("@")[0]
    parts = [p for p in re.split(r"[._-]+", local) if p]
    return " ".join(p.capitalize() for p in parts) or local


def _people(s):
    """Everyone who will hold a seat on day one: the invitees plus you."""
    return len(_invites(s)) + 1


def _selected_plan(s):
    return LbPlan.objects.filter(slug=s.plan).first() if s.plan else None


def _validate_step(s, step, strict=False):
    """Gentle while typing, strict when the step tries to advance.

    Step 3 validates against answers given on step 2 — the seat check only works
    because the invites are still in the signal bag when the plan is chosen.
    """
    errors = {}

    if step == 1:
        if s.workspace_name.strip():
            if len(s.workspace_name.strip()) < 3:
                errors["name"] = "Give the workspace a name with at least 3 characters."
        elif strict:
            errors["name"] = "Name your workspace."

        slug = s.workspace_slug.strip()
        if slug:
            if not SLUG_RE.match(slug):
                errors["slug"] = "Lowercase letters, numbers and hyphens only."
            elif LbWorkspace.objects.filter(slug=slug).exists():
                errors["slug"] = "That address is taken. Try another."
        elif strict:
            errors["slug"] = "Choose the address your team will sign in at."

    elif step == 2:
        for i in INVITE_SLOTS:
            email = getattr(s, f"invite_{i}").strip()
            if not email:
                continue
            if not EMAIL_RE.match(email):
                errors[f"invite_{i}"] = "That does not look like an email address."
            elif LbMember.objects.filter(email=email).exists():
                errors[f"invite_{i}"] = f"{email} is already on an Arden workspace."
        if strict and not _invites(s):
            errors["invites"] = "Invite at least one teammate — Arden is worth more with the revenue team in it."

    elif step == 3:
        plan = _selected_plan(s)
        if plan is None:
            if strict:
                errors["plan"] = "Choose a plan to finish setting up."
        else:
            people = _people(s)
            if people > plan.seats_included:
                errors["plan"] = (
                    f"{plan.name} includes {plan.seats_included} seats and you are starting with "
                    f"{people}. Pick a larger plan, or remove an invite."
                )

    return errors


def _invite_slots(s, errors):
    """One row per invite field, carrying everything the row needs to render."""
    slots = []
    for i in INVITE_SLOTS:
        email = getattr(s, f"invite_{i}").strip()
        slots.append(
            {
                "n": i,
                "path": f"form.invite_{i}",
                "email": email,
                "initials": _initials(email) if EMAIL_RE.match(email) else "",
                "placeholder": INVITE_PLACEHOLDERS[i - 1],
                "error": errors.get(f"invite_{i}", ""),
            }
        )
    return slots


def _ctx(s, errors=None, workspace=None, members=None):
    errors = errors or {}
    invites = [
        {"email": e, "initials": _initials(e), "name": _display_name(e)} for e in _invites(s)
    ]
    return {
        "signals": s,
        "step": s.step,
        "invite_slots": _invite_slots(s, errors),
        "total_steps": TOTAL_STEPS,
        "regions": REGIONS,
        "roles": ROLES,
        "plans": LbPlan.objects.all(),
        "selected_plan": _selected_plan(s),
        "invites": invites,
        "people": _people(s),
        "trial_days": TRIAL_DAYS,
        "errors": errors,
        "created": workspace is not None,
        "workspace": workspace,
        "members": members or [],
    }


def _page(request, ctx):
    return render_page(request, INDEX, ctx, title=TITLE)


def index(request):
    return _page(request, _ctx(OnboardingSignals(request)))


def validate(request):
    """Live, gentle validation of the step the user is on. No step change."""
    s = OnboardingSignals(request)
    return _page(request, _ctx(s, errors=_validate_step(s, s.step)))


def next_step(request):
    s = OnboardingSignals(request)
    errors = _validate_step(s, s.step, strict=True)
    if errors:
        return _page(request, _ctx(s, errors=errors))
    s.step = min(s.step + 1, TOTAL_STEPS)
    return _page(request, _ctx(s))


def prev_step(request):
    s = OnboardingSignals(request)
    s.step = max(s.step - 1, 1)
    return _page(request, _ctx(s))


def submit(request):
    if request.method != "POST":
        return index(request)

    s = OnboardingSignals(request)
    for step in range(1, TOTAL_STEPS + 1):
        errors = _validate_step(s, step, strict=True)
        if errors:
            s.step = step
            return _page(request, _ctx(s, errors=errors))

    today = timezone.now().date()
    workspace = LbWorkspace.objects.create(
        name=s.workspace_name.strip(),
        slug=s.workspace_slug.strip(),
        plan=_selected_plan(s),
        region=s.region,
        currency="USD",
        billing_email=_invites(s)[0],
        trial_ends_on=today + datetime.timedelta(days=TRIAL_DAYS),
        created_at=timezone.now(),
    )
    members = [
        LbMember.objects.create(
            workspace=workspace,
            name=_display_name(email),
            email=email,
            title="",
            role=s.invite_role,
            status="invited",
            joined_on=today,
        )
        for email in _invites(s)
    ]
    return _page(request, _ctx(s, workspace=workspace, members=members))
