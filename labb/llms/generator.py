"""
LLM documentation generator.

This module generates concise documentation specifically formatted for LLMs,
following the llms.txt standard for token efficiency.
"""

from labb.components.registry import ComponentRegistry


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

    # Generate component descriptions first
    component_descriptions = generate_component_descriptions()

    content = f"""# labb - Django Component Library

labb is a Django component library providing components built with Django Cotton and styled with Tailwind CSS + daisyUI 5.

## Key Features
- **Django Cotton Integration**: HTML-like component syntax
- **Backend Rendered**: Server-side rendering for fast loads and SEO
- **No JavaScript Required**: Components work without JS by default
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
- Main commands: `init`, `setup`, `dev`, `build`, `scan`, `components`, `icons`, `llms`
- Development workflow: `labb dev` (watches files and rebuilds automatically)
- Component inspection: `labb components inspect <component>` (shows specs, variables, types)
- View examples: `labb components ex <component> [example1] [example2]` (shows raw HTML code)
- Browse all examples: `labb components ex --tree` (hierarchical view of all examples)
- Icon management: `labb icons search/packs/info` (requires labbicons package)
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
    'ALPINE_JS_PATH': 'labb/js/alpine/alpine.min.js',  # or a CDN URL
    'STACK_HELPERS': {{
        'components': ['labb/js/alpine/labb-component.js', 'alpine'],
    }},
}}
```

- `DEFAULT_THEME`: any daisyUI theme defined in your `input.css`. `"__system__"` defers to OS preference.
- `ALPINE_JS_PATH`: path or full URL to Alpine.js. Defaults to the bundled file.
- `STACK_HELPERS`: maps stack names to helper scripts. `"alpine"` is a special token that emits a deferred script tag using `ALPINE_JS_PATH`.

**Access settings in code:**
```python
from labb.django_settings import get_labb_setting, get_default_theme

theme = get_labb_setting('DEFAULT_THEME')
default_theme = get_default_theme()
```

## Reactivity
labb components are zero-JS by default. Reactivity is opt-in via Alpine.js using `.x` component variants.

**How it works:**
- Use `<c-lb.button.x>` instead of `<c-lb.button>` to get a reactive version
- Each `.x` component registers an Alpine data object; use `this.lbProps` inside extended components to read/write reactive props
- Scripts only load when `.x` components are actually used on the page — Alpine is never included otherwise
- Props with a CSS class mapping (marked with `*` in these docs) can be changed at runtime
— For sub-components, use dot notation (e.g. `<c-lb.stat.group.x>`)

**Basic usage:**
```html
<!-- Static initial props (server-rendered) -->
<c-lb.button.x variant="primary" size="lg">Save</c-lb.button.x>

<!-- Runtime binding with x-model -->
<div x-data="{{ btn: {{ variant: 'primary', size: 'md' }} }}">
    <c-lb.button.x x-model="btn" variant="primary" size="md">
        Click me
    </c-lb.button.x>
    <select x-model="btn.variant">
        <option value="primary">Primary</option>
        <option value="error">Error</option>
    </select>
</div>
```

**Prop format:** plain JS object with camelCase keys matching schema variable names (e.g. `{{ variant: '', btnStyle: '', size: 'md' }}`). Empty string means no value.

**Extending a reactive component** with custom state and methods:
```js
document.addEventListener('alpine:init', () => {{
    Alpine.data('myComp', lb.extendComponent('button', {{
        loading: false,
        save() {{ this.lbProps.variant = 'success'; }}
    }}));
}});
```
Pass the extended factory as `x-data` on the `.x` component. Sub-components use dot notation: `lb.extendComponent('stat.group', {{ ... }})`.

**Force-load Alpine** (for pages using Alpine without `.x` components):
```html
<c-lb.m.dependencies alpine />
```

**Setup:** ensure `<c-lb.m.dependencies />` is in your base `<head>`. No other config needed.

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
Chart components accept `x-model` natively — no `.x` variant needed. Bind to an object with `data`, `options`, and/or `legend`; reassign the whole object to trigger an update.
```html
<div x-data="{{ cfg: {{ data: {{ labels: [...], datasets: [...] }} }},
               randomize() {{ this.cfg = {{ data: {{ ... }} }}; }} }}">
    <c-lb.button @click="randomize()">Shuffle</c-lb.button>
    <c-lb.chart.bar x-model="cfg" />
</div>
```

**Theme switching:** charts destroy + rebuild automatically when `<html data-theme>` changes, so all DaisyUI-named colours re-resolve without a refresh.

## Components
Props marked with `*` are reactive — they can be changed at runtime via the `.x` variant (e.g. `<c-lb.button.x>`).
{component_descriptions}
"""

    return content


if __name__ == "__main__":
    # When run directly, generate and write the file
    from labb.llms.file_operations import write_llms_txt

    output_path = write_llms_txt()
    print(f"✅ Generated llms.txt at: {output_path}")
