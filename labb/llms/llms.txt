# labb - Django Component Library

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
    <h2>{{ title }}</h2>
    {{ slot }}
</div>

<!-- Usage in templates -->
<c-card title="My Card">
    <p>Card content here</p>
</c-card>
```

See: https://django-cotton.com/ for complete Django Cotton documentation.

## Quick Start
```html
{% load lb_tags %}
<!DOCTYPE html>
<html data-theme="{% labb_theme %}">
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
LABB_SETTINGS = {
    'DEFAULT_THEME': 'labb-light',       # Default theme for new users
    'ALPINE_JS_PATH': 'labb/js/alpine/alpine.min.js',  # or a CDN URL
    'STACK_HELPERS': {
        'components': ['labb/js/alpine/labb-component.js', 'alpine'],
    },
}
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
<div x-data="{ btn: { variant: 'primary', size: 'md' } }">
    <c-lb.button.x x-model="btn" variant="primary" size="md">
        Click me
    </c-lb.button.x>
    <select x-model="btn.variant">
        <option value="primary">Primary</option>
        <option value="error">Error</option>
    </select>
</div>
```

**Prop format:** plain JS object with camelCase keys matching schema variable names (e.g. `{ variant: '', btnStyle: '', size: 'md' }`). Empty string means no value.

**Extending a reactive component** with custom state and methods:
```js
document.addEventListener('alpine:init', () => {
    Alpine.data('myComp', lb.extendComponent('button', {
        loading: false,
        save() { this.lbProps.variant = 'success'; }
    }));
});
```
Pass the extended factory as `x-data` on the `.x` component. Sub-components use dot notation: `lb.extendComponent('stat.group', { ... })`.

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
{% load lb_tags %}
<!-- Base template -->
<html {% labb_theme %}>
<head>
    <c-lb.m.dependencies setThemeEndpoint="{% url 'set_theme' %}" />
</head>
<body>
    {% csrf_token %}  <!-- REQUIRED: Add CSRF token for theme switching -->
    <!-- Your content here -->
</body>
```

**IMPORTANT:** Always include `{% csrf_token %}` in your main template body when using theme controllers. The theme switching functionality requires CSRF protection for POST requests.

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
- `{% labb_theme %}` - Template tag for current theme (adds data-theme attribute)

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
<c-lb.chart.bar data='{
    "labels": ["Jan", "Feb", "Mar"],
    "datasets": [{ "label": "Revenue", "data": [10, 20, 30] }]
}' />
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
<c-lb.chart.polar-area data='{
    "labels": ["Design", "Development", "Testing"],
    "datasets": [{
        "data": [40, 75, 60],
        "backgroundColor": ["primary", "secondary", "accent"],
        "borderWidth": 0
    }]
}' />
```

**Reactivity:**
Chart components accept `x-model` natively — no `.x` variant needed. Bind to an object with `data`, `options`, and/or `legend`; reassign the whole object to trigger an update.
```html
<div x-data="{ cfg: { data: { labels: [...], datasets: [...] } },
               randomize() { this.cfg = { data: { ... } }; } }">
    <c-lb.button @click="randomize()">Shuffle</c-lb.button>
    <c-lb.chart.bar x-model="cfg" />
</div>
```

**Theme switching:** charts destroy + rebuild automatically when `<html data-theme>` changes, so all DaisyUI-named colours re-resolve without a refresh.

## Components
Props marked with `*` are reactive — they can be changed at runtime via the `.x` variant (e.g. `<c-lb.button.x>`).
**accordion**: Accordion component for displaying collapsible content sections | Vars: class: string, join*: boolean | 5 examples
**accordion.item**: Individual accordion item with collapsible content | Vars: style*: arrow/plus, class: string, name: string, checked*: boolean
**alert**: Alert component for displaying important messages with various styles and colors | Vars: variant*: info/success/warning/error, class: string, alertStyle*: outline/dash/soft, direction*: vertical/horizontal | 10 examples
**avatar**: Avatar component for displaying user thumbnails or profile pictures | Vars: size*: xs/sm/md/lg/xl, class: string, rounded*: xs/sm/md/lg/xl/full, mask*: heart/squircle/hexagon-2/triangle/pentagon/diamond/star | 11 examples
**avatar.group**: Group wrapper for multiple avatars with overlapping layout | Vars: class: string, spacing*: wide/normal/tight/tighter/tightest
**badge**: Badge component for displaying status, counts, or labels | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, style*: outline/dash/soft/ghost, size*: xs/sm/md/lg/xl, class: string, icon: string, icon.class: string | 11 examples
**breadcrumbs**: Breadcrumbs navigation component for displaying current page location in site hierarchy | Vars: size*: xs/sm/md/lg/xl, class: string | 7 examples
**breadcrumbs.item**: Individual breadcrumb item with optional link and icon support | Vars: class: string, href: string, viewname: string
**button**: Button component with different styles and sizes | Vars: as: button/a/input/div, variant*: neutral/primary/secondary/accent/info/success/warning/error, behavior*: active/disabled, size*: xs/sm/md/lg/xl, class: string, btnStyle*: outline/dash/soft/ghost/link/bare | 13 examples
**card**: Main card container component with support for various layouts and styles | Vars: variant*: default/primary/secondary/accent/neutral/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string, border*: boolean, dash*: boolean | 11 examples
**card.actions**: Container for action elements (e.g., buttons) | Vars: class: string, justify*: start/center/end/between/around/evenly
**card.body**: Main content area of the card | Vars: class: string
**card.figure**: Image container within the card | Vars: class: string
**card.title**: Title section within the card body | Vars: as: h1/h2/h3/h4/h5/h6/div/span, class: string
**carousel**: Carousel component for displaying scrollable content with snap behavior | Vars: class: string, snap*: start/center/end, direction*: horizontal/vertical | 7 examples
**carousel.item**: Individual carousel item container | Vars: class: string, id: string
**chart**: Optional page-level provider. Sets Chart.js global defaults and enables live DaisyUI theme switching for all charts on the page. | Vars: color: string, grid: boolean, animation: boolean | 23 examples
**chart.bar**: Bar chart. Datasets are auto-coloured from the DaisyUI palette. Redraws on theme change. | Vars: class: string, height: string, legend: top/bottom/left/right/none
**chart.bubble**: Bubble chart. Each dataset requires {x, y, r} point objects where r is the radius in pixels. Bubbles are auto-coloured from the DaisyUI palette. | Vars: class: string, height: string, legend: top/bottom/left/right/none
**chart.doughnut**: Doughnut chart. Slices are auto-coloured from the DaisyUI palette. | Vars: class: string, height: string, legend: top/bottom/left/right/none
**chart.instance**: Generic chart proxy. Renders any Chart.js type via the type prop. Used internally by all chart sub-components. | Vars: class: string, height: string, legend: top/bottom/left/right/none
**chart.line**: Line chart. Smooth lines with point markers. Supports fill areas and auto-palette colouring. | Vars: class: string, height: string, legend: top/bottom/left/right/none
**chart.pie**: Pie chart. Slices are auto-coloured from the DaisyUI palette. | Vars: class: string, height: string, legend: top/bottom/left/right/none
**chart.polar-area**: Polar area chart. Slices are auto-coloured from the DaisyUI palette. | Vars: class: string, height: string, legend: top/bottom/left/right/none
**chart.radar**: Radar (spider) chart. Datasets are auto-coloured from the DaisyUI palette. | Vars: class: string, height: string, legend: top/bottom/left/right/none
**chart.scatter**: Scatter chart. Each dataset requires {x, y} point objects. Points are auto-coloured from the DaisyUI palette. | Vars: class: string, height: string, legend: top/bottom/left/right/none
**chat**: Chat container for a single message in a conversation thread | Vars: class: string, placement*: start/end | 3 examples
**chat.bubble**: Message bubble that displays the chat message text | Vars: variant*: primary/secondary/accent/neutral/info/success/warning/error, class: string
**chat.footer**: Footer text displayed below the chat bubble, typically showing delivery status or timestamp | Vars: class: string
**chat.header**: Header text displayed above the chat bubble, typically showing the sender name | Vars: class: string
**chat.image**: Avatar image displayed alongside the chat message | Vars: size*: sm/md/lg, class: string, src: string, alt: string
**checkbox**: Checkbox input component with various styles and states | Vars: variant*: primary/secondary/accent/neutral/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string, validate*: boolean | 4 examples
**collapse**: Standalone expandable section with a title and collapsible content area | Vars: style*: arrow/plus, class: string, open*: boolean, title: string | 4 examples
**diff**: Image comparison component with draggable resizer for before/after views | Vars: class: string, aspectRatio*: 16/9/4/3/1/1/3/4/9/16 | 5 examples
**diff.item-1**: First item in the diff comparison (typically the 'before' image) | Vars: class: string, src: string, alt: string
**diff.item-2**: Second item in the diff comparison (typically the 'after' image) | Vars: class: string, src: string, alt: string
**diff.resizer**: Draggable resizer control for adjusting the comparison view | Vars: class: string
**divider**: Divider line to separate content | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, class: string, direction*: horizontal/vertical, position*: start/end | 4 examples
**dock**: Bottom navigation dock component for mobile app-style navigation | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string | 3 examples
**dock.label**: Text label for a dock navigation item | Vars: class: string
**drawer**: Main drawer wrapper component - use with drawer sub-components for full functionality | Vars: drawerId: string, class: string, end*: boolean | 13 examples
**drawer.checkbox**: Drawer toggle checkbox input - controls drawer open/close state | Vars: class: string
**drawer.content**: Drawer main content area - contains the primary page content | Vars: as: div/main/section/article, class: string
**drawer.overlay**: Drawer overlay label - provides backdrop for closing the drawer | Vars: class: string
**drawer.side**: Drawer sidebar container - wraps the sidebar content and overlay | Vars: class: string
**drawer.toggle**: Drawer toggle label - provides a clickable label for the drawer checkbox | Vars: class: string, for: string
**dropdown**: Dropdown component that shows content when focused or clicked | Vars: class: string, placement*: bottom/top/left/right, alignment*: start/center/end | 6 examples
**dropdown.content**: Dropdown content container that appears when dropdown is active | Vars: class: string
**dropdown.trigger**: Dropdown trigger button that controls the dropdown visibility | Vars: as: div/button/label, class: string
**fab**: FAB (Floating Action Button) with Speed Dial functionality | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string, flower*: boolean, icon: string | 16 examples
**fab.close**: FAB close button sub-component | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string
**fab.main-action**: FAB main action button sub-component | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string
**fieldset**: Container for grouping related form elements with an optional legend | Vars: class: string, legend: string | 3 examples
**fieldset.legend**: Legend/title for a fieldset group | Vars: class: string
**file-input**: Styled file upload input | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string, ghost*: boolean, validate*: boolean | 4 examples
**filter**: Radio or checkbox button group for filtering content | Vars: as: div/form, class: string, multiSelect: boolean | 3 examples
**filter.item**: Individual filter radio button | Vars: class: string, name: string, label: string
**footer**: Footer component for displaying site footer content with optional centered layout | Vars: as: footer/div/section, class: string, center*: boolean, direction*: horizontal/vertical | 9 examples
**footer.title**: Footer section title component - applies footer-title styling | Vars: as: span/h2/h3/h4/h5/h6/div/p, class: string
**hero**: Hero section with content and optional overlay | Vars: class: string, overlay*: boolean | 3 examples
**hero.content**: Content wrapper inside hero | Vars: class: string
**hero.overlay**: Overlay layer for hero background images | Vars: class: string
**hover-gallery**: CSS-only image gallery that reveals different images on hover across horizontal columns | Vars: as: figure/div, class: string | 3 examples
**hover3d**: CSS-only 3D tilt effect wrapper using 8 hover-zone divs to detect mouse position and apply rotation | Vars: class: string | 2 examples
**indicator**: Container that positions an indicator item on a child element | Vars: class: string | 6 examples
**indicator.item**: Item positioned on corner of sibling element | Vars: variant: neutral/primary/secondary/accent/info/success/warning/error, size: xs/sm/md/lg/xl, class: string, shape: badge/status/none, horizontal*: start/center/end
**input**: Styled text input field | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string, ghost*: boolean, validate*: boolean | 4 examples
**join**: Groups multiple items together visually | Vars: class: string, direction*: horizontal/vertical | 3 examples
**kbd**: Keyboard key indicator to display keyboard shortcuts or key combinations | Vars: size*: xs/sm/md/lg/xl, variant*: neutral/primary/secondary/accent/info/success/warning/error, class: string, icon: string, icon.class: string | 9 examples
**label**: Descriptive text label for form inputs | Vars: as: p/span/label/div, class: string, floating: boolean | 2 examples
**link**: Link component with support for href, Django view name resolution, DaisyUI styling, and l: prefixed URL arguments | Vars: as: a/button/span/div, variant*: neutral/primary/secondary/accent/info/success/warning/error, class: string, href: string, viewname: string | 5 examples
**list**: List component for displaying information in vertical rows with horizontal layout | Vars: as: ul/div/ol, class: string | 2 examples
**list.row**: Individual list row item with horizontal grid layout | Vars: as: li/div, class: string
**loading**: Loading spinner/animation indicator | Vars: size*: xs/sm/md/lg/xl, variant*: neutral/primary/secondary/accent/info/success/warning/error, class: string, type*: spinner/dots/ring/ball/bars/infinity | 3 examples
**mask**: Applies mask shape to crop content | Vars: class: string, shape*: squircle/heart/hexagon/hexagon-2/decagon/pentagon/diamond/square/circle/star/star-2/triangle/triangle-2/triangle-3/triangle-4, half*: 1/2 | 2 examples
**menu**: Flexible navigation menu component with support for horizontal/vertical layout and sizes | Vars: size*: xs/sm/md/lg/xl, class: string, direction*: vertical/horizontal | 12 examples
**menu.item**: Unified menu item supporting links, titles, and submenus with choice of details/summary or ul/li | Vars: size*: xs/sm/md/lg/xl, class: string, type*: link/title/submenu-details/submenu-toggle, title: string
**mockup-browser**: Browser window mockup | Vars: class: string, url: string | 1 examples
**mockup-code**: Code terminal mockup | Vars: class: string | 2 examples
**mockup-phone**: Phone device mockup | Vars: class: string | 2 examples
**mockup-phone.camera**: Phone camera notch | Vars: class: string
**mockup-phone.display**: Phone display area | Vars: class: string, img: string, alt: string
**mockup-window**: OS window mockup | Vars: class: string | 1 examples
**modal**: Modal dialog component using HTML dialog element for better accessibility | Vars: size: map, class: string, id: string, placement*: top/middle/bottom/start/end | 13 examples
**modal.action**: Container for modal action buttons | Vars: class: string
**modal.backdrop**: Backdrop overlay for closing modal when clicked outside | Vars: class: string
**modal.box**: Main content container for the modal | Vars: size*: xs/sm/md/lg/xl/screen, class: string
**modal.close**: Close button for modal | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, class: string, position*: top-right/top-left/bottom-right/bottom-left
**navbar**: Responsive navigation bar component with support for brand, menu items, search, and profile sections | Vars: as: div/nav/header, class: string | 8 examples
**navbar.center**: Center section of the navbar - typically contains main navigation links (works within navbar context) | Vars: as: div/section/nav, class: string
**navbar.end**: Right section of the navbar - typically contains search, notifications, and profile (works within navbar context) | Vars: as: div/section/aside, class: string
**navbar.start**: Left section of the navbar - typically contains brand and mobile menu toggle (works within navbar context) | Vars: as: div/section/aside, class: string
**pagination**: Pagination component using join group for page navigation | Vars: class: string | 4 examples
**pagination.item**: Individual pagination button item | Vars: size*: xs/sm/md/lg/xl, class: string, active*: boolean, disabled*: boolean
**progress**: Progress bar to show completion status | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, class: string, value: string, max: string | 3 examples
**radial-progress**: Circular progress indicator using CSS variables | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, class: string, bgVariant*: neutral/primary/secondary/accent/info/success/warning/error, value: string | 4 examples
**radio**: Radio button input component | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string, validate*: boolean | 3 examples
**range**: Range slider input | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string, validate*: boolean | 4 examples
**rating**: Star rating input using radio buttons | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string, name: string, max: string | 4 examples
**select**: Styled dropdown select input | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string, ghost*: boolean, validate*: boolean | 3 examples
**skeleton**: Placeholder element with loading animation | Vars: as: div/span, class: string, text*: boolean | 3 examples
**stack**: Stacks child elements on top of each other | Vars: class: string, direction*: top/bottom/start/end | 2 examples
**stat**: Individual stat block for displaying a metric with optional title, value, description, and figure | Vars: class: string | 5 examples
**stat.actions**: Container for action elements within a stat | Vars: class: string
**stat.desc**: Description or subtitle for the stat metric | Vars: variant*: primary/secondary/accent/neutral/info/success/warning/error, class: string
**stat.figure**: Container for icon or image displayed with the stat | Vars: variant*: primary/secondary/accent/neutral/info/success/warning/error, class: string, icon: string, icon.class: string
**stat.group**: Container for grouping multiple stat components with horizontal or vertical layout | Vars: class: string, direction*: horizontal/vertical
**stat.title**: Title or label for the stat metric | Vars: class: string
**stat.value**: Primary value display for the stat metric | Vars: variant*: primary/secondary/accent/neutral/info/success/warning/error, class: string
**status**: Small status indicator icon to show current state like online, offline, or error | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string, animate*: ping/bounce | 3 examples
**steps**: Steps component for showing progress through a multi-step process | Vars: class: string, direction*: horizontal/vertical | 5 examples
**steps.item**: Individual step in a steps sequence | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, class: string, content: string, icon: string
**swap**: Swap component for toggling between two elements with smooth transitions | Vars: class: string, effect*: rotate/flip, checked*: boolean | 8 examples
**swap.indeterminate**: Content shown when checkbox is in indeterminate state | Vars: class: string, icon: string, icon.class: string
**swap.off**: Content shown when swap is inactive | Vars: class: string, icon: string, icon.class: string
**swap.on**: Content shown when swap is active | Vars: class: string, icon: string, icon.class: string
**table**: DaisyUI Table component with support for zebra, pinning, and sizes. | Vars: size*: xs/sm/md/lg/xl, class: string, zebra*: boolean, pinRows*: boolean | 4 examples
**tabs**: Main tabs wrapper component - use with tabs.content for full functionality | Vars: style*: border/lift/box, size*: xs/sm/md/lg/xl, class: string, placement*: top/bottom, name: string | 6 examples
**tabs.content**: Individual tab content with radio input and content area | Vars: class: string, name: string, checked*: boolean
**text**: Text component with support for variants, sizes, underline, and icons | Vars: as: span/p/div/h1/h2/h3/h4/h5/h6, variant*: neutral/primary/secondary/accent/info/success/warning/error, size*: xs/sm/md/lg/xl/2xl/3xl/4xl, class: string, underline*: boolean, icon: string | 9 examples
**text-rotate**: Text rotation component that cycles through multiple text items with animation | Vars: class: string, duration: string | 4 examples
**textarea**: Styled multi-line text input | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string, ghost*: boolean, validate*: boolean | 3 examples
**timeline**: Timeline component for displaying chronological events | Vars: class: string, direction*: horizontal/vertical, compact*: boolean | 8 examples
**timeline.end**: Content positioned at the end side of a timeline item | Vars: class: string, box*: boolean
**timeline.hr**: Connector line between timeline items | Vars: class: string
**timeline.item**: Individual timeline event item with automatic hr connectors and convenience props for start, middle, and end content | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, class: string, first: boolean, last: boolean
**timeline.middle**: Central icon or marker area of a timeline item | Vars: class: string, icon: string, icon.class: string
**timeline.start**: Content positioned at the start side of a timeline item | Vars: class: string, box*: boolean
**toast**: Fixed-position container for toast notifications | Vars: class: string, horizontal*: start/center/end, vertical*: top/middle/bottom | 2 examples
**toggle**: Toggle switch component for boolean input | Vars: variant*: primary/secondary/accent/neutral/info/success/warning/error, size*: xs/sm/md/lg/xl, class: string, checked*: boolean, disabled*: boolean | 6 examples
**tooltip**: Tooltip component that shows text or custom content on hover | Vars: variant*: neutral/primary/secondary/accent/info/success/warning/error, class: string, tip: string, placement*: top/bottom/left/right | 4 examples
**tooltip.content**: Custom HTML content for tooltip (alternative to data-tip text) | Vars: class: string
**validator.hint**: Hint text shown when a validated input is invalid | Vars: class: string, hidden*: boolean
