from django.utils import timezone

from labb.contrib.blocks import lm, render_page
from labb.signals import Bool, Signals, Str

LbMember = lm("LbMember")
LbWorkspace = lm("LbWorkspace")

SIGN_IN = "lb/auth/split-brand/pages/sign_in.html"
SIGN_UP = "lb/auth/split-brand/pages/sign_up.html"

MIN_PASSWORD = 8


class AuthSignals(Signals):
    name      = Str(path="form.name",     default="")
    email     = Str(path="form.email",    default="")
    password  = Str(path="form.password", default="")
    submitted = Bool(path="submitted",    default=False)


def _validate(s, strict=False, with_name=False):
    """Gentle while typing, strict on submit.

    One validator serves both sign-in and sign-up — the only difference is
    whether a name is expected, which is what makes a single view able to back
    both pages.
    """
    errors = {}

    if with_name:
        if s.name:
            if len(s.name.strip()) < 2:
                errors["name"] = "Enter your full name."
        elif strict:
            errors["name"] = "Name is required."

    if s.email:
        if "@" not in s.email or "." not in s.email.split("@")[-1]:
            errors["email"] = "Enter a valid email address."
    elif strict:
        errors["email"] = "Email is required."

    if s.password:
        if len(s.password) < MIN_PASSWORD:
            errors["password"] = f"At least {MIN_PASSWORD} characters ({len(s.password)} so far)."
    elif strict:
        errors["password"] = "Password is required."

    return errors


def _ctx(signals, errors=None, submitted=False, member=None, failed=""):
    return {
        "signals": signals,
        "errors": errors or {},
        "submitted": submitted,
        "member": member,
        "failed": failed,
    }


def _page(request, template, ctx, title):
    return render_page(request, template, ctx, title=title)


# --- sign in ---------------------------------------------------------------

def index(request):
    return _page(request, SIGN_IN, _ctx(AuthSignals(request)), "Sign in to Arden")


def validate(request):
    s = AuthSignals(request)
    return _page(request, SIGN_IN, _ctx(s, errors=_validate(s)), "Sign in to Arden")


def submit(request):
    if request.method != "POST":
        return index(request)

    s = AuthSignals(request)
    errors = _validate(s, strict=True)
    if errors:
        return _page(request, SIGN_IN, _ctx(s, errors=errors), "Sign in to Arden")

    member = LbMember.objects.filter(email=s.email).select_related("workspace").first()
    if member is None:
        return _page(
            request,
            SIGN_IN,
            _ctx(s, failed="No Arden account found for that email."),
            "Sign in to Arden",
        )

    s.submitted = True
    return _page(request, SIGN_IN, _ctx(s, submitted=True, member=member), "Sign in to Arden")


# --- sign up ---------------------------------------------------------------

def sign_up(request):
    return _page(request, SIGN_UP, _ctx(AuthSignals(request)), "Create an Arden account")


def sign_up_validate(request):
    s = AuthSignals(request)
    return _page(
        request,
        SIGN_UP,
        _ctx(s, errors=_validate(s, with_name=True)),
        "Create an Arden account",
    )


def sign_up_submit(request):
    if request.method != "POST":
        return sign_up(request)

    s = AuthSignals(request)
    errors = _validate(s, strict=True, with_name=True)
    if errors:
        return _page(request, SIGN_UP, _ctx(s, errors=errors), "Create an Arden account")

    if LbMember.objects.filter(email=s.email).exists():
        return _page(
            request,
            SIGN_UP,
            _ctx(s, failed="That email is already on an Arden workspace."),
            "Create an Arden account",
        )

    workspace = LbWorkspace.objects.first()
    member = LbMember.objects.create(
        workspace=workspace,
        name=s.name.strip(),
        email=s.email,
        title="",
        role="member",
        status="invited",
        joined_on=timezone.now().date(),
        last_active_at=timezone.now(),
    )

    s.submitted = True
    return _page(
        request,
        SIGN_UP,
        _ctx(s, submitted=True, member=member),
        "Create an Arden account",
    )
