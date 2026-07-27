"""
LLM documentation generator.

This module generates concise documentation specifically formatted for LLMs,
following the llms.txt standard for token efficiency.
"""

from pathlib import Path

from labb.components.registry import ComponentRegistry

DOCS_BASE_URL = "https://labb.io"

# Sections whose pages are worth citing from llms.txt. Each doc page is also
# available as raw markdown by appending .md to its URL.
REFERENCE_SECTIONS = [
    ("guide", "3_reactivity", "Reactivity"),
    ("guide", "4_references", "Reference"),
    ("guide", "5_about", "About"),
]


def _page_url(doc_name: str, relative_path: str) -> str:
    """Map a content file path to its published .md URL.

    "3_reactivity/2_signals.md" -> "/docs/guide/reactivity/signals.md"
    """
    parts = []
    for segment in relative_path.replace(".md", "").split("/"):
        if "_" in segment and segment.split("_")[0].isdigit():
            segment = "_".join(segment.split("_")[1:])
        parts.append(segment.replace("_", "-"))
    prefix = "/blog" if doc_name == "blog" else f"/docs/{doc_name}"
    return f"{DOCS_BASE_URL}{prefix}/{'/'.join(parts)}.md"


def _content_root():
    """The labbdocs content directory, when generating from a repo checkout."""
    root = Path(__file__).resolve().parents[2] / "docs" / "labbdocs" / "content"
    return root if root.is_dir() else None


def generate_doc_references() -> str:
    """List the doc pages worth reading in full, as raw-markdown URLs.

    Reactivity is far too broad to inline here; these are the pages to fetch
    when the summary above is not enough. Derived from the content tree, so new
    pages appear without editing this module.
    """
    root = _content_root()
    if root is None:
        return ""

    blocks = []
    for doc_name, section, title in REFERENCE_SECTIONS:
        section_dir = root / doc_name / section
        if not section_dir.is_dir():
            continue
        lines = []
        for md in sorted(section_dir.glob("*.md")):
            relative = f"{section}/{md.name}"
            lines.append(f"- {_page_url(doc_name, relative)}")
        if lines:
            blocks.append(f"### {title}\n" + "\n".join(lines))

    if not blocks:
        return ""

    return (
        "\n## Further Reading\n"
        "Every doc page is available as raw markdown by appending `.md` to its URL. "
        "Fetch these when the summaries above are not enough — reactivity in particular "
        "is covered in far more depth than fits here.\n\n"
        + "\n\n".join(blocks)
        + "\n"
    )




def generate_component_descriptions() -> str:
    """Generate component descriptions using the ComponentRegistry"""

    registry = ComponentRegistry()
    components = registry.get_all_components()

    if not components:
        return "No components available."

    descriptions = []

    for name, spec in sorted(components.items()):
        # Get basic info
        description = spec.get("description", "").strip()

        # Get key variables (limit to most important ones)
        variables = spec.get("variables", {})
        key_vars = []

        # Prioritize certain variable types
        priority_vars = ["variant", "size", "style", "as", "behavior"]
        other_vars = []

        for var_name, var_spec in variables.items():
            var_type = var_spec.get("type", "string")
            reactive = "*" if var_spec.get("css_mapping") else ""

            # Format variable info concisely
            if var_type == "enum" and "values" in var_spec:
                values = [str(v) for v in var_spec["values"] if str(v).strip()]
                if values:
                    var_info = f"{var_name}{reactive}: {'/'.join(values)}"
                else:
                    continue
            elif var_type == "boolean":
                var_info = f"{var_name}{reactive}: boolean"
            else:
                var_info = f"{var_name}{reactive}: {var_type}"

            if var_name in priority_vars:
                key_vars.append(var_info)
            else:
                other_vars.append(var_info)

        # Combine priority and other vars, limit total
        all_vars = key_vars + other_vars[:3]  # Max 3 additional vars
        vars_text = ", ".join(all_vars[:6])  # Max 6 total vars

        # Get example count
        examples = registry.get_component_example_names(name)
        example_count = len(examples)

        # Build component description
        comp_desc = f"**{name}**: {description}"

        if vars_text:
            comp_desc += f" | Vars: {vars_text}"

        if example_count > 0:
            comp_desc += f" | {example_count} examples"

        descriptions.append(comp_desc)

    return "\n".join(descriptions)


def generate_llms_txt() -> str:
    """Generate the complete llms.txt content."""

    component_descriptions = generate_component_descriptions()
    doc_references = generate_doc_references()

    content = f"""# labb - Django Component Library

labb is a Django component library providing components built with Django Cotton and styled with Tailwind CSS + daisyUI 5.

## Key Features
- **Django Cotton Integration**: HTML-like component syntax
- **Backend Rendered**: Server-side rendering for fast loads and SEO
- **No JavaScript Required**: Components work without JS by default
- **Opt-in Reactivity**: Datastar-powered signals, reactive props, and server actions load only on pages that use them
- **Blocks**: 35 installable UI blocks across 7 surfaces (auth, dashboard, data-table, hero, pricing, settings, wizard)
- **Theme Support**: Built-in light/dark themes with custom theme creation
- **CLI Tool**: `labb` command for project setup, CSS building, and component scanning

## Installation
1. Install: `pip install labbui` or `poetry add labbui`
2. Add 'django_cotton', 'labb' to INSTALLED_APPS
3. Initialize project (from Django project root): `labb init --defaults`
4. Install dependencies: `labb setup --install-deps`
5. Start development: `labb dev`

## labbstart (Project Scaffolding)
**labbstart** scaffolds a new Django project with labb pre-configured. Use it for the fastest way to get started.

- Install: `pip install labbstart` or `poetry add labbstart` or `uv add labbstart`
- Create project: `labbstart new` (interactive) or `labbstart new myproject --django-version 5 --package-manager poetry --kit welcome --app-name starter`
- Prompts for: project name, Django version (4/5/6), package manager (poetry/pip/uv), kit (e.g. welcome), app name
- Creates: project dir, package manager setup, Django + labbui + labbicons, starter kit app, labb init + build, .gitignore, README
- After creation: run `labb dev` in one terminal and `python manage.py runserver` in another
- Requirements: Python 3.10+ (<4), and poetry/pip/uv

## Icons (Optional)
Install labbicons for icon support: `pip install labbicons` or `poetry add labbicons`

**Icon Usage:**
- Search icons: `labb icons search "arrow"`
- List packs: `labb icons packs`
- Get icon info: `labb icons info rmx.arrow-down`
- Use in components that supports icon: `<c-lb.button icon="rmx.arrow-down">Button</c-lb.button>`
- Direct icon usage: `<c-lbi.rmx.arrow-down w="3" h="3" />`

**Icon Dot-Notation Modifiers:**
Components that support `icon` also support dot-notation modifiers in the attribute name:
- `icon="name"` — line (outlined) icon at start
- `icon.fill="name"` — filled (solid) icon
- `icon.end="name"` — icon at end (button, badge, text, pagination.item)
- `icon.fill.end="name"` — filled icon at end (modifiers combine, order doesn't matter)
- `icon.class="classes"` — additional CSS classes for the icon (separate attribute, does not combine with fill/end)

```html
<c-lb.button icon="rmx.home">Home</c-lb.button>
<c-lb.button icon.fill="rmx.heart" variant="error">Like</c-lb.button>
<c-lb.button icon.end="rmx.arrow-right">Next</c-lb.button>
<c-lb.button icon.fill.end="rmx.check" variant="success">Done</c-lb.button>
<c-lb.button icon="rmx.star" icon.class="text-warning">Favorite</c-lb.button>
```

**Direct icon usage** (for full control over size, attributes):
```html
<c-lb.badge variant="success">
  <c-lbi n="rmx.check" w="1em" h="1em" />
  Success
</c-lb.badge>
```

## Django Cotton
Django Cotton enables HTML-like component syntax in Django templates. labb components are built with this system. Components are reusable template fragments that accept parameters and slots.

```html
<!-- Component definition: templates/cotton/card.html -->
<div class="card">
    <h2>{{{{ title }}}}</h2>
    {{{{ slot }}}}
</div>

<!-- Usage in templates -->
<c-card title="My Card">
    <p>Card content here</p>
</c-card>
```

See: https://django-cotton.com/ for complete Django Cotton documentation.

## Quick Start
```html
{{% load lb_tags %}}
<!DOCTYPE html>
<html data-theme="{{% labb_theme %}}">
<head>
    <c-lb.m.dependencies />
</head>
<body>
    <c-lb.button variant="primary">Click me</c-lb.button>
    <c-lb.card>
        <c-lb.card.body>
            <c-lb.card.title>Card Title</c-lb.card.title>
            <p>Content here</p>
        </c-lb.card.body>
    </c-lb.card>
</body>
</html>
```

## CLI Help
- Get help: `labb --help` or `labb <command> --help`
- Main commands: `init`, `setup`, `dev`, `build`, `scan`, `components`, `icons`, `block`, `llms`
- Development workflow: `labb dev` (watches files and rebuilds automatically)
- Component inspection: `labb components inspect <component>` (shows specs, variables, types)
- View examples: `labb components ex <component> [example1] [example2]` (shows raw HTML code)
- Browse all examples: `labb components ex --tree` (hierarchical view of all examples)
- Icon management: `labb icons search/packs/info` (requires labbicons package)
- Block management: `labb block list/search/add/sync/remove` (installable UI blocks)
- Display llms.txt content for AI/LLM consumption: `labb llms`

## Configuration (labb.yaml)
The `labb.yaml` file controls CSS building and template scanning:

```yaml
css:
  build:
    input: static_src/input.css    # Input CSS file
    output: static/css/output.css  # Output CSS file
    minify: true                   # Minify output
  scan:
    output: static_src/labb-classes.txt  # Extracted classes file
    templates:                           # Template patterns to scan
      - templates/**/*.html
      - '*/templates/**/*.html'
```

**Override with CLI:**
```bash
labb build --input src/styles.css --output dist/app.css
labb scan --output src/classes.txt --patterns "templates/**/*.html"
```

**Environment variable:** `LABB_CONFIG_PATH` to override config file location

## Django Settings
Configure labb settings in your Django `settings.py`:

```python
LABB_SETTINGS = {{
    'DEFAULT_THEME': 'labb-light',       # Default theme for new users
}}
```

- `DEFAULT_THEME`: any daisyUI theme defined in your `input.css`. `"__system__"` defers to OS preference.

**Access settings in code:**
```python
from labb.django_settings import get_labb_setting, get_default_theme

theme = get_labb_setting('DEFAULT_THEME')
default_theme = get_default_theme()
```

## Reactivity
This is a summary. The full treatment — signals, reactive props, events and bindings, server actions, morphing — is in the reactivity guide; see Further Reading at the end for the raw-markdown URLs of each page.

labb components are zero-JS by default. Labb reactivity is opt-in and uses two complementary tools: **signal props** for client-side state binding, and **reactivity directives** for server-driven interactions. Both rely on Datastar under the hood; static pages ship zero JavaScript.

**Setup:** add `ReactivityMiddleware` to your `MIDDLEWARE` in `settings.py`:
```python
MIDDLEWARE = [
    ...
    'labb.middleware.ReactivityMiddleware',
    ...
]
```
Ensure `<c-lb.m.dependencies />` is in your base `<head>`. The `lb-schema.js` bundle loads automatically when `c-lbr.signals` is present on the page.

### Signal props
Signal props bind any labb component prop to a Datastar signal at the client level. Prefix a prop value with `$` to enable the binding; the `:fallback` value is server-rendered on first paint.

**Declare signals:**
```html
<c-lbr.signals $ui.variant="neutral" />
```

**Bind to a component prop:**
```html
<c-lb.badge variant="$ui.variant:neutral">Status</c-lb.badge>
```
The syntax is `"$signal.path:fallback"`. The fallback after `:` is used for the initial server render.

**Read signals in a Django view:**
```python
from labb.signals import Signals, Str

class MySignals(Signals):
    variant = Str(default="neutral")

def my_view(request):
    signals = MySignals.from_request(request)
    current_variant = signals.variant   # e.g. "success"
    ...
```

**Update signals from a view** (before rendering):
```python
signals.variant = "success"
context = {{"signals": signals, ...}}
return render(request, "my_template.html", context)
```

### Reactivity directives
Reactivity directives (`c-lbr.*`) drive server-side interactions. On the triggering event labb fetches a normal Django view; Datastar morphs the full-page HTML response in place. No partials and no JSON are required.

| Directive | What it does |
|---|---|
| `c-lbr.signals` | Declares initial signal values |
| `c-lbr.get` | Fetches a URL on an event (default: click) |
| `c-lbr.post` | Posts form data to a URL |
| `c-lbr.delete` | Sends DELETE to a URL |
| `c-lbr.replace-url` | Updates the browser URL without navigation |
| `c-lbr.target` | Scopes a morph to a specific DOM element |

**Example — fetch on click:**
```html
<c-lbr.get url="{{% url 'my_view' %}}" event="click">
    <c-lb.button variant="primary">Refresh</c-lb.button>
</c-lbr.get>
```

## Blocks
Blocks are ready-made, installable slices of UI built from labb components. Some are frontend-only markup; others are full features that ship models, views, urls, fixtures, and templates. You add a block into your own project with the `labb block` CLI, then own and edit the vendored code.

**Catalogue:** 35 blocks across 7 surfaces (5 each): `auth`, `dashboard`, `data-table`, `hero`, `pricing`, `settings`, `wizard`.

**Workflow:**
```bash
labb block list                 # list all blocks from configured sources
labb block search "dashboard"   # search by name or description
labb block init                 # initialise a block collection as a Django app
labb block add <surface/slug>   # add a block into your collection
labb block sync <surface/slug>  # re-fetch and overwrite vendored code from source
labb block remove <surface/slug>
labb block source               # manage block sources
labb block dev                  # block authoring and development tools
```

Blocks are reactive where it makes sense (search, sort, filter, inline edit) using the same Datastar signal props and `c-lbr.*` directives described above. Full-feature blocks wire their own `views.py` and `urls.py`, which you include from your project urls.

## General Rules
- Boolean attributes can be set implicitly to true by just adding them (no need for `="true"`)
  - Example: `<c-lb.button disabled>` instead of `<c-lb.button disabled="true">`

## Theming
labb provides built-in theming with daisyUI 5 integration:

**Quick Setup:**
```html
{{% load lb_tags %}}
<!-- Base template -->
<html {{% labb_theme %}}>
<head>
    <c-lb.m.dependencies setThemeEndpoint="{{% url 'set_theme' %}}" />
</head>
<body>
    {{% csrf_token %}}  <!-- REQUIRED: Add CSRF token for theme switching -->
    <!-- Your content here -->
</body>
```

**IMPORTANT:** Always include `{{% csrf_token %}}` in your main template body when using theme controllers. The theme switching functionality requires CSRF protection for POST requests.

**URL Configuration:**
```python
# urls.py
from labb.shortcuts import set_theme_view
path('set-theme/', set_theme_view, name='set_theme')
```

**Theme Controller:**
```html
<!-- Toggle switch -->
<c-lb.toggle class="theme-controller" value="labb-dark" />

<!-- Checkbox -->
<c-lb.checkbox class="theme-controller" value="labb-dark" />
```

**Available Themes:** `labb-light`, `labb-dark`, `light` (daisyUI's built-in theme), `dark` (daisyUI's built-in theme), plus any custom themes defined in `input.css`

**Utility Functions:**
- `labb.shortcuts.set_labb_theme(request, theme)` - Set theme in session
- `labb.shortcuts.get_labb_theme(request)` - Get current theme
- `{{% labb_theme %}}` - Template tag for current theme (adds data-theme attribute)

## AI/LLM Usage Guidelines
**ALWAYS USE THE CLI FIRST** when working with labb components, especially when stuck with an issue:

```bash
# Get exact component specifications (parameters, types, defaults)
labb components inspect <component>

# See working examples with correct syntax
labb components ex <component>

# View specific examples to copy exact syntax (supports multiple examples)
labb components ex <component> <example-name> <example-name> ...

# Explore all available components and examples
labb components ex --tree
```

**Why Use CLI:**
- Get exact parameter names (e.g., `btnStyle` not `style`)
- See all available options and built-in features
- Copy tested, working syntax
- Avoid parameter name mistakes and missing features

**Common Mistakes to Avoid:**
- DON'T guess parameter names - Use `labb components inspect`
- DON'T guess icon names - Use `labb icons search "term"` or `labb llms` to find exact icon names. Guessing (e.g. `rmx.rocket-2-line`) often causes: `TypeError: cannot unpack non-iterable NoneType object` when the icon does not exist.
- DON'T create manual icons - Use built-in `icon="rmx.iconname"` (search with `labb icons search`)
- DON'T skip CLI examples - They show correct syntax

**Common Errors:**
- `TypeError: cannot unpack non-iterable NoneType object` at docs or UI routes: Usually caused by an invalid or guessed icon name (e.g. `rmx.rocket-2-line` when the actual icon is `rmx.rocket-2`). Fix: Run `labb icons search "keyword"` or `labb llms` to find the correct icon name; use the exact "Component" value from search results (e.g. `rmx.rocket-2`).

## Charts
Charts are rendered with Chart.js and themed with DaisyUI. Each chart type has a dedicated component (`<c-lb.chart.bar>`, `<c-lb.chart.line>`, `<c-lb.chart.pie>`, `<c-lb.chart.doughnut>`, `<c-lb.chart.radar>`, `<c-lb.chart.polar-area>`, `<c-lb.chart.scatter>`, `<c-lb.chart.bubble>`) that accepts Chart.js `data` and `options` as JSON strings.

**Basic usage:**
```html
<c-lb.chart.bar data='{{
    "labels": ["Jan", "Feb", "Mar"],
    "datasets": [{{ "label": "Revenue", "data": [10, 20, 30] }}]
}}' />
```

**Dataset colours — DaisyUI name conventions:**
Pass colour names directly in `backgroundColor` / `borderColor`; they resolve at render time and re-resolve on theme change.
- `"primary"`, `"secondary"`, `"accent"`, `"info"`, `"success"`, `"warning"`, `"error"`, `"neutral"`, `"base-100"`..`"base-300"`, `"base-content"` — live DaisyUI CSS variable
- `"primary-light"` (any name + `-light` suffix) — same colour at reduced alpha (controlled by `lightAlpha`, default `0.4`); ideal for fills under a solid `borderColor`
- `"--color-custom"` — any CSS custom property
- `"#hex"`, `"rgb(...)"`, `"oklch(...)"`, named CSS colours — passed through unchanged; `-light` suffix also works on raw colours via `color-mix`

**Auto-palette:** if a dataset has no `backgroundColor` / `borderColor`, slices/datasets cycle through `primary → secondary → accent → info → success → warning → error`. `polarArea` and `radar` use `-light` fills + solid borders by default; `pie`, `doughnut`, `bar`, `line` use solid fills.

**Page-level config (`<c-lb.chart />` provider):**
Drop once on a page (or base template) to override global Chart.js defaults for every chart below it. All props are optional.
```html
<c-lb.chart color="base-content" :grid="False" animation updateAnimation
            fontSize="12" tooltips legend lightAlpha="0.4" />
```
- `color` — label/axis/legend text colour (DaisyUI name, `--color-x`, or any CSS colour)
- `grid` — show grid lines on cartesian scales (default off)
- `animation` — entry animation (set `:animation="False"` for PDFs / large datasets)
- `updateAnimation` — animate reactive data updates (set False for live feeds)
- `fontSize` — pixel font size for axes/legend/tooltips
- `tooltips`, `legend` — global on/off
- `lightAlpha` — alpha applied to all `*-light` colour variants

**Per-dataset overrides:**
Anything you put in `data` or `options` is merged on top of labb's defaults, so you can always opt out. Example — solid vibrant polar slices with no border:
```html
<c-lb.chart.polar-area data='{{
    "labels": ["Design", "Development", "Testing"],
    "datasets": [{{
        "data": [40, 75, 60],
        "backgroundColor": ["primary", "secondary", "accent"],
        "borderWidth": 0
    }}]
}}' />
```

**Reactivity:**
Chart components update reactively via signal props. Bind a chart's `data` prop to a signal declared with `c-lbr.signals`; updating the signal (e.g. via a reactivity directive) causes the chart to re-render without a full page reload.
```html
<c-lbr.signals $chart.data='{{ "labels": [...], "datasets": [...] }}' />
<c-lb.chart.bar data="$chart.data:{{}}" />
<c-lbr.get url="{{% url 'refresh_chart' %}}" event="click">
    <c-lb.button>Shuffle</c-lb.button>
</c-lbr.get>
```

**Theme switching:** charts destroy + rebuild automatically when `<html data-theme>` changes, so all DaisyUI-named colours re-resolve without a refresh.

## Components
Props marked with `*` have a CSS class mapping — they can be driven at runtime via signal props (e.g. `variant="$ui.variant:neutral"`).
{component_descriptions}
{doc_references}
"""

    return content


if __name__ == "__main__":
    # When run directly, generate and write the file
    from labb.llms.file_operations import write_llms_txt

    output_path = write_llms_txt()
    print(f"✅ Generated llms.txt at: {output_path}")
