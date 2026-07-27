import re

from datastar_py.consts import ElementPatchMode
from django.shortcuts import redirect
from django.utils import timezone

from labb.contrib.blocks import lm, render_page
from labb.reactivity import SSEResponse, patch_component
from labb.signals import Signals, Str

LbInvoice = lm("LbInvoice")
LbMember = lm("LbMember")
LbPlan = lm("LbPlan")
LbWorkspace = lm("LbWorkspace")

INDEX = "lb/settings/workspace/pages/index.html"
INNER = ElementPatchMode.INNER
TITLE = "Workspace settings"

REGIONS = [
    ("eu-west-1", "Europe (Ireland)"),
    ("us-east-1", "US East (Virginia)"),
    ("ap-south-1", "Asia Pacific (Mumbai)"),
]

INVITE_ROLES = [
    ("admin", "Admin — can change billing and members"),
    ("member", "Member — full access to customers and invoices"),
    ("billing", "Billing — invoices and payment methods only"),
    ("viewer", "Viewer — read-only"),
]

ROLE_VARIANTS = {
    "owner": "primary",
    "admin": "secondary",
    "billing": "accent",
    "member": "neutral",
    "viewer": "neutral",
}

STATUS_VARIANTS = {"active": "success", "invited": "warning", "suspended": "error"}

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MIN_SLUG = 3


class ProfileSignals(Signals):
    name   = Str(path="profile.name",   default="")
    slug   = Str(path="profile.slug",   default="")
    email  = Str(path="profile.email",  default="")
    region = Str(path="profile.region", default="")


class InviteSignals(Signals):
    email = Str(path="invite.email", default="")
    role  = Str(path="invite.role",  default="member")


# --- data ------------------------------------------------------------------

def _workspace():
    return LbWorkspace.objects.select_related("plan").first()


def _initials(name):
    parts = [p for p in name.split() if p]
    return "".join(p[0] for p in parts[:2]).upper() or "?"


def _members(workspace):
    members = list(workspace.members.all())
    for m in members:
        m.initials = _initials(m.name)
        m.role_variant = ROLE_VARIANTS.get(m.role, "neutral")
        m.status_variant = STATUS_VARIANTS.get(m.status, "neutral")
    return members


def _seats_used(members):
    """A suspended member is not billed, so they do not hold a seat."""
    return sum(1 for m in members if m.status != "suspended")


def _looks_like_email(value):
    return "@" in value and "." in value.split("@")[-1] and len(value.split("@")[-1]) > 3


# --- validation ------------------------------------------------------------

def _profile_errors(s, workspace, strict=False):
    """Gentle while typing, strict on save."""
    errors = {}

    if s.name:
        if len(s.name.strip()) < 2:
            errors["name"] = "Workspace names need at least two characters."
    elif strict:
        errors["name"] = "A workspace name is required."

    if s.slug:
        if not SLUG_RE.match(s.slug):
            errors["slug"] = "Lowercase letters, numbers and single hyphens only."
        elif len(s.slug) < MIN_SLUG:
            errors["slug"] = f"At least {MIN_SLUG} characters ({len(s.slug)} so far)."
        elif LbWorkspace.objects.exclude(pk=workspace.pk).filter(slug=s.slug).exists():
            errors["slug"] = "Another workspace already uses that address."
    elif strict:
        errors["slug"] = "A workspace address is required."

    if s.email:
        if not _looks_like_email(s.email):
            errors["email"] = "Enter a valid billing email."
    elif strict:
        errors["email"] = "Invoices need somewhere to go."

    return errors


def _invite_errors(s, workspace, strict=False):
    errors = {}

    if s.email:
        if not _looks_like_email(s.email):
            errors["email"] = "Enter a valid work email."
        else:
            existing = LbMember.objects.filter(email__iexact=s.email).first()
            if existing is not None:
                errors["email"] = f"{existing.name} is already on this workspace."
    elif strict:
        errors["email"] = "Enter the email of the person you want to invite."

    return errors


# --- section props ---------------------------------------------------------
#
# One dict per section, shared by the full-page render and the scoped patch, so
# a zone can never drift between the two.

def _profile_signals(request, workspace):
    s = ProfileSignals(request)
    if not request.signals:
        s.name = workspace.name
        s.slug = workspace.slug
        s.email = workspace.billing_email
        s.region = workspace.region
    return s


def _profile_props(request, workspace, errors=None):
    return {
        "workspace": workspace,
        "signals": _profile_signals(request, workspace),
        "errors": errors or {},
        "regions": REGIONS,
    }


def _team_props(request, workspace, errors=None):
    members = _members(workspace)
    seats_used = _seats_used(members)
    seats_total = workspace.plan.seats_included
    return {
        "workspace": workspace,
        "members": members,
        "seats_used": seats_used,
        "seats_total": seats_total,
        "seats_left": max(0, seats_total - seats_used),
        "seats_full": seats_used >= seats_total,
        "seats_pct": min(100, round(seats_used * 100 / seats_total)) if seats_total else 0,
        "plan": workspace.plan,
        "signals": InviteSignals(request),
        "errors": errors or {},
        "roles": INVITE_ROLES,
    }


def _billing_props(request, workspace, failed=""):
    invoices = list(
        LbInvoice.objects.filter(customer__workspace=workspace).select_related("customer")[:5]
    )
    for inv in invoices:
        inv.status_variant = {"paid": "success", "open": "info", "overdue": "error"}.get(
            inv.status, "neutral"
        )
    outstanding = sum(
        inv.amount
        for inv in LbInvoice.objects.filter(
            customer__workspace=workspace, status__in=("open", "overdue")
        )
    )
    plans = list(LbPlan.objects.all())
    for p in plans:
        p.is_current = p.pk == workspace.plan_id

    return {
        "workspace": workspace,
        "plan": workspace.plan,
        "plans": plans,
        "invoices": invoices,
        "outstanding": f"{outstanding:,.2f}",
        "billing_contacts": [m for m in workspace.members.filter(role="billing")],
        "failed": failed,
    }


def _context(request, workspace):
    if workspace is None:
        return {"workspace": None}
    return {
        "workspace": workspace,
        "profile_signals": _profile_signals(request, workspace),
        "invite_signals": InviteSignals(request),
        "profile": _profile_props(request, workspace),
        "team": _team_props(request, workspace),
        "billing": _billing_props(request, workspace),
    }


# --- patches ---------------------------------------------------------------

def _patch_profile(request, workspace, errors=None):
    return patch_component(
        request, "@section-profile", "workspace.profile",
        mode=INNER, **_profile_props(request, workspace, errors),
    )


def _patch_team(request, workspace, errors=None):
    return patch_component(
        request, "@section-team", "workspace.team",
        mode=INNER, **_team_props(request, workspace, errors),
    )


def _patch_billing(request, workspace, failed=""):
    return patch_component(
        request, "@section-billing", "workspace.billing",
        mode=INNER, **_billing_props(request, workspace, failed),
    )


def _patch_toast(request, message, detail=""):
    return patch_component(
        request, "@toast", "workspace.toast",
        mode=INNER, message=message, detail=detail,
    )


# --- views -----------------------------------------------------------------

def index(request):
    return render_page(request, INDEX, _context(request, _workspace()), title=TITLE)


def profile_validate(request):
    workspace = _workspace()
    if workspace is None:
        return redirect("block_settings_workspace:index")
    s = _profile_signals(request, workspace)
    errors = _profile_errors(s, workspace)
    return SSEResponse([_patch_profile(request, workspace, errors)])


def profile_save(request):
    workspace = _workspace()
    if request.method != "POST" or workspace is None:
        return redirect("block_settings_workspace:index")

    s = _profile_signals(request, workspace)
    errors = _profile_errors(s, workspace, strict=True)
    if errors:
        return SSEResponse([_patch_profile(request, workspace, errors)])

    workspace.name = s.name.strip()
    workspace.slug = s.slug.strip()
    workspace.billing_email = s.email.strip()
    workspace.region = s.region or workspace.region
    workspace.save()

    return SSEResponse([
        _patch_profile(request, workspace),
        _patch_toast(request, "Profile saved", f"{workspace.name} · arden.app/w/{workspace.slug}"),
    ])


def invite_validate(request):
    workspace = _workspace()
    if workspace is None:
        return redirect("block_settings_workspace:index")
    s = InviteSignals(request)
    return SSEResponse([_patch_team(request, workspace, _invite_errors(s, workspace))])


def invite_save(request):
    workspace = _workspace()
    if request.method != "POST" or workspace is None:
        return redirect("block_settings_workspace:index")

    s = InviteSignals(request)
    errors = _invite_errors(s, workspace, strict=True)

    props = _team_props(request, workspace)
    if props["seats_full"]:
        errors["email"] = (
            f"All {props['seats_total']} seats on {workspace.plan.name} are in use. "
            "Change plan to add more."
        )

    if errors:
        return SSEResponse([_patch_team(request, workspace, errors)])

    email = s.email.strip()
    member = LbMember.objects.create(
        workspace=workspace,
        name=email.split("@")[0].replace(".", " ").title(),
        email=email,
        title="",
        role=s.role,
        status="invited",
        joined_on=timezone.now().date(),
        last_active_at=None,
    )

    s.email = ""
    return SSEResponse([
        s.patch("email"),
        _patch_team(request, workspace),
        _patch_toast(request, "Invite sent", f"{member.email} joins as {member.get_role_display()}."),
    ])


def plan_change(request, pk):
    workspace = _workspace()
    if request.method != "POST" or workspace is None:
        return redirect("block_settings_workspace:index")

    plan = LbPlan.objects.filter(pk=pk).first()
    if plan is None or plan.pk == workspace.plan_id:
        return SSEResponse([_patch_billing(request, workspace)])

    seats_used = _seats_used(_members(workspace))
    if seats_used > plan.seats_included:
        failed = (
            f"{plan.name} includes {plan.seats_included} seats and {seats_used} are in use. "
            "Remove members first, or stay on your current plan."
        )
        return SSEResponse([_patch_billing(request, workspace, failed)])

    workspace.plan = plan
    workspace.save()
    workspace = _workspace()

    # The seat allowance shown in the team section comes from the plan, so that
    # zone is genuinely affected too — patch every zone the change touches, and
    # only those.
    return SSEResponse([
        _patch_billing(request, workspace),
        _patch_team(request, workspace),
        _patch_toast(request, "Plan changed", f"You are now on {plan.name}."),
    ])
