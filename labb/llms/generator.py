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

            # Format variable info concisely
            if var_type == "enum" and "values" in var_spec:
                values = [str(v) for v in var_spec["values"] if str(v).strip()]
                if values:
                    var_info = f"{var_name}: {'/'.join(values)}"  # Show all values
                else:
                    continue
            elif var_type == "boolean":
                var_info = f"{var_name}: boolean"
            else:
                var_info = f"{var_name}: {var_type}"

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

## Icons (Optional)
Install labbicons for icon support: `pip install labbicons` or `poetry add labbicons`

**Icon Usage:**
- Search icons: `labb icons search "arrow"`
- List packs: `labb icons packs`
- Get icon info: `labb icons info rmx.arrow-down`
- Use in components that supports icon: `<c-lb.button icon="rmx.arrow-down">Button</c-lb.button>`
- Direct icon usage: `<c-lbi.rmx.arrow-down w="3" h="3" />`

**Examples:**
```html
<!-- Badge with integrated icon -->
<c-lb.badge variant="info" icon="rmx.information">Info</c-lb.badge>

<!-- Badge with direct icon usage -->
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
    'DEFAULT_THEME': 'default',  # Default theme for new users
}}
```

`DEFAULT_THEME` can be set to `default` or any daisyUI theme configured in your project's `input.css`.

**Access settings in code:**
```python
from labb.django_settings import get_labb_setting, get_default_theme

theme = get_labb_setting('DEFAULT_THEME', 'default')
default_theme = get_default_theme()
```

## General Rules
- Boolean attributes can be set implicitly to true by just adding them (no need for `="true"`)
  - Example: `<c-lb.button disabled>` instead of `<c-lb.button disabled="true">`

## Theming
labb provides built-in theming with daisyUI 5 integration:

**Quick Setup:**
```html
{{% load lb_tags %}}
<!-- Base template -->
<html data-theme="{{% labb_theme %}}">
<head>
    <c-lb.m.dependencies setThemeEndpoint="{{% url 'set_theme' %}}" />
</head>
```

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
- `{{% labb_theme %}}` - Template tag for current theme

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
- DON'T create manual icons - Use built-in `icon="rmx.iconname"` (search with `labb icons search`)
- DON'T skip CLI examples - They show correct syntax

## Components
{component_descriptions}
"""

    return content


if __name__ == "__main__":
    # When run directly, generate and write the file
    from labb.llms.file_operations import write_llms_txt

    output_path = write_llms_txt()
    print(f"✅ Generated llms.txt at: {output_path}")
