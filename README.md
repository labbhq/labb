![labb welcome kit](docs/labbdocs/static/lbdocs/img/labb/labb_welcome_kit.jpg)

# labb

UI components library for Django perfectionists.

Built on [django-cotton](https://github.com/wrabit/django-cotton), [Tailwind CSS](https://tailwindcss.com/), and [DaisyUI 5](https://daisyui.com/).

## Why labb?

Django templates are powerful, but building consistent UI means writing the same markup patterns over and over. labb gives you a growing collection of ready-to-use components that work like native HTML elements in your templates -- no JavaScript framework required.

```html
<c-lb.button variant="primary">Save changes</c-lb.button>

<c-lb.card border>
    <c-lb.card.body>
        <c-lb.card.title>Django components, done right</c-lb.card.title>
        <p>Composable, themeable, and fully server-rendered.</p>
        <c-lb.card.actions>
            <c-lb.button variant="primary">Get started</c-lb.button>
        </c-lb.card.actions>
    </c-lb.card.body>
</c-lb.card>

<c-lb.modal id="confirm" withBackdrop withCloseBtn>
    <h3>Are you sure?</h3>
    <p>This action cannot be undone.</p>
    <c-lb.modal.action>
        <c-lb.button variant="error">Delete</c-lb.button>
    </c-lb.modal.action>
</c-lb.modal>
```

## Features

- **Variant-driven API** -- control style through props like `variant`, `size`, and `btnStyle`, not CSS classes
- **Composable** -- nest components naturally with slots and named slots (`<c-lb.card.body>`, `<c-lb.modal.action>`)
- **Server-rendered** -- no JavaScript runtime, no virtual DOM, just Django templates
- **Icon support** -- optional `labbicons` package with multiple icon packs (`<c-lbi n="rmx.heart" />`)
- **CLI tooling** -- inspect components, search icons, build CSS, and scaffold projects from the terminal
- **Python 3.10 - 3.13** and **Django 4.2+**

## Getting started

The fastest way to start a new project with labb is `labbstart`:

```bash
pip install labbstart
labbstart new myproject
```

This scaffolds a complete Django project with labb, Tailwind CSS, and DaisyUI pre-configured -- ready to run in one command. It supports Poetry, pip, and uv, and includes a welcome page to get you oriented.

### Adding to an existing project

```bash
pip install labbui

# With icons
pip install labbui[icons]
```

Add to your Django settings:

```python
INSTALLED_APPS = [
    "django_cotton",
    "labb",
    # ...
]
```

## Quick examples

### Buttons

```html
<c-lb.button>Default</c-lb.button>
<c-lb.button variant="primary" size="lg">Large primary</c-lb.button>
<c-lb.button variant="error" btnStyle="outline">Delete</c-lb.button>
<c-lb.button as="a" href="/docs">Link styled as button</c-lb.button>
<c-lb.button variant="success" icon="rmx.check-line">Confirm</c-lb.button>
```

### Dropdown

```html
<c-lb.dropdown>
    <c-lb.dropdown.trigger>
        <c-lb.button>Options</c-lb.button>
    </c-lb.dropdown.trigger>
    <c-lb.dropdown.content>
        <c-lb.menu>
            <c-lb.menu.item>Edit</c-lb.menu.item>
            <c-lb.menu.item>Duplicate</c-lb.menu.item>
            <c-lb.menu.item>Archive</c-lb.menu.item>
        </c-lb.menu>
    </c-lb.dropdown.content>
</c-lb.dropdown>
```

### Tabs

```html
<c-lb.tabs variant="bordered">
    <c-lb.tabs.content label="Overview" checked>
        <p>Overview content here.</p>
    </c-lb.tabs.content>
    <c-lb.tabs.content label="Settings">
        <p>Settings content here.</p>
    </c-lb.tabs.content>
</c-lb.tabs>
```

### Alert with icon

```html
<c-lb.alert variant="info" icon="rmx.information-line">
    Your changes have been saved.
</c-lb.alert>
```

## CLI

labb ships with a CLI for inspecting components, searching icons, and managing your build:

```bash
labb components inspect --list     # List all available components
labb components inspect button -v  # Inspect a component's API
labb components ex button          # View component examples
labb icons search "arrow"          # Search icon packs
labb build -w                      # Watch and build CSS
labb init --defaults               # Scaffold a new project
```

## Documentation

Full documentation is available at [labb.io](https://labb.io/).

## License

MIT License
