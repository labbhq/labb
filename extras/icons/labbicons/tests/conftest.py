import django
from django.conf import settings


def pytest_configure():
    """Configure Django without pytest-django.

    The suite only renders templates, so it needs settings and an app registry,
    not a database.
    """
    if not settings.configured:
        import labbicons.tests.settings as test_settings

        settings.configure(
            **{k: v for k, v in vars(test_settings).items() if k.isupper()}
        )
    django.setup()
