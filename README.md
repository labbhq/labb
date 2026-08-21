# labb

labb is a UI component library for Django, built with [django-cotton](https://django-cotton.com/), Tailwind CSS, and daisyUI 5. Write components directly in Django templates; labb renders the markup on the server.

It includes 50+ components for forms, navigation, data display, feedback, layouts, and charts. Pages stay static by default. When a page needs browser state or server-driven updates, labb uses Datastar while keeping Django views and templates in charge.

**Requirements:** Python 3.10–3.13 and Django 4.2+.

> **Status:** labb is in pre-stable development and ready for production use. The 0.5.0 release settled the main API changes, so breaking changes should now be uncommon before v1.0.

```html
<c-lb.card class="w-80">
    <c-lb.card.body>
        <c-lb.card.title>New order</c-lb.card.title>
        <p>Ready for review.</p>
        <c-lb.button variant="primary">Open order</c-lb.button>
    </c-lb.card.body>
</c-lb.card>
```

## Start a new project

```bash
pip install labbstart
labbstart new
cd your-project-name
labb dev
```

Run `python manage.py runserver` in another terminal, then open <http://localhost:8000>.

## Add labb to an existing project

```bash
pip install labbui
labb init --defaults
labb setup
```

Add the apps to `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    "django_cotton",
    "labb",
]
```

Add the dependencies component inside your base template's `<head>`:

```html
{% load lb_tags %}
<c-lb.m.dependencies />
```

Keep `labb dev` running while you work. Install icons with `pip install labbui[icons]` when you need them.

## Explore components

Browse examples and API references at [labb.io/docs/ui](https://labb.io/docs/ui/), or inspect components from the terminal:

```bash
labb components inspect button
labb components ex button
labb icons search "arrow"
```

The [guide](https://labb.io/docs/guide/) covers installation, theming, CSS builds, reactivity, and writing your own components.

## Community

Follow [GitHub Discussions](https://github.com/labbhq/labb/discussions) for release notes and project updates. We use Discussions for questions and feedback..

## License

[MIT](LICENSE)
