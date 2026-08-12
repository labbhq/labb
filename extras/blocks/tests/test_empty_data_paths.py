"""Block views against databases that are empty or only partly seeded."""

import json

import pytest
from django.apps import apps
from django.utils import timezone

LbWorkspace = apps.get_model("lb", "LbWorkspace")
LbMember = apps.get_model("lb", "LbMember")

SIGN_UP_SUBMIT = "/lb/auth/split-brand/preview/sign-up/submit/"
TEAM_PAGE = "/lb/settings/workspace/preview/"
TEAM_INVITE = "/lb/settings/workspace/preview/team/invite/"


def _signals(**form):
    return json.dumps({"form": form, "submitted": False})


def _post(client, url, **form):
    return client.post(url, data=_signals(**form), content_type="application/json")


def _workspace(plan=None):
    return LbWorkspace.objects.create(
        name="Arden",
        slug="arden",
        plan=plan,
        region="eu-west-1",
        currency="USD",
        billing_email="ops@arden.test",
        trial_ends_on=timezone.now().date(),
        created_at=timezone.now(),
    )


@pytest.mark.django_db
def test_sign_up_without_a_workspace_does_not_500(client):
    resp = _post(
        client,
        SIGN_UP_SUBMIT,
        name="Ada Lovelace",
        email="ada@example.com",
        password="hunter2hunter2",
    )
    assert resp.status_code == 200
    assert not LbMember.objects.exists()


@pytest.mark.django_db
def test_sign_up_with_a_duplicate_email_does_not_500(client):
    workspace = _workspace()
    LbMember.objects.create(
        workspace=workspace,
        name="Ada Lovelace",
        email="ada@example.com",
        title="",
        role="member",
        status="active",
        joined_on=timezone.now().date(),
    )
    resp = _post(
        client,
        SIGN_UP_SUBMIT,
        name="Ada Lovelace",
        email="ada@example.com",
        password="hunter2hunter2",
    )
    assert resp.status_code == 200
    assert LbMember.objects.count() == 1


@pytest.mark.django_db
def test_team_page_renders_for_a_workspace_with_no_plan(client):
    _workspace(plan=None)
    assert client.get(TEAM_PAGE).status_code == 200


@pytest.mark.django_db
def test_team_invite_on_a_planless_workspace_does_not_500(client):
    _workspace(plan=None)
    resp = client.post(
        TEAM_INVITE,
        data=json.dumps({"invite": {"email": "new@example.com", "role": "member"}}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    assert not LbMember.objects.exists()
