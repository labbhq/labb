---
title: labb.yaml
description: "labb.yaml configuration for Django projects: paths, Tailwind CSS, daisyUI themes, and labb CLI defaults."
keywords: "labb.yaml, labb config django, labb project configuration"
---

{% load docs_tags %}

The `labb.yaml` configuration file controls most aspects of your labb project. This file is created when you run `labb init` and is used by all labb CLI commands.

## Default configuration

The default structure of a `labb.yaml` file created by `labb init`:

```yaml
css:
  build:
    input: static_src/input.css
    output: static/css/output.css
    minify: true
  packages:
    labb: [themes, components]   # CSS groups pulled from installed packages
  scan:
    templates:                   # your own templates, scanned for <c-lb.*> usage
      - templates/**/*.html
      - '*/templates/**/*.html'
      - '**/templates/**/*.html'
```

## Configuration sections

### CSS build configuration

Controls how CSS is built using Tailwind CSS 4 when using the <a href="{% doc_url '5_references/0_labb_cli.md' 'guide' %}#labb-build">`labb build`</a> command:

```yaml
css:
  build:
    input: static_src/input.css    # Input CSS file path
    output: static/css/output.css  # Output CSS file path
    minify: true                   # Whether to minify CSS output
```

These settings can be overridden using command-line parameters:

```bash
# Override input/output files
labb build --input src/styles.css --output dist/app.css

# Override minification setting
labb build --no-minify
```

### CSS packages configuration

`css.packages` declares which **installed packages** contribute CSS to your build. A package publishes named **groups**; you subscribe to the ones you need. Everything is import-resolved, so it works whether the package is a path dependency or installed from PyPI. You never hardcode another package's file paths.

```yaml
css:
  packages:
    labb: [themes, blocks]        # named groups from the labb package
    labbdocs: [docs]
    other: '*'                    # every group the package publishes
    custom:                       # raw form (for a package that publishes no groups)
      components: [templates/**/*.html]   # usage-scanned for <c-lb.*> variant classes
      literals:   [templates/**/*.html]   # handed to Tailwind as @source (raw utilities)
      imports:    [css/extra.css]         # package CSS inlined into the build
```

Each package entry is one of: a **list of group names**, `'*'` (or the `all` alias, or blank) for every group, or a **raw mapping** of `components` / `literals` / `imports`. Selected groups are merged (duplicate globs and imports collapse).

The three contribution kinds:

- **`components`**: templates scanned for `<c-lb.*>` usage; their variant classes go into the safelist (`.labb/labb-component-classes.txt`).
- **`literals`**: templates handed to Tailwind as `@source`, so the raw utility classes written literally in the markup compile.
- **`imports`**: CSS files shipped inside the package, inlined into the build (labb's themes arrive this way).

All three land in a single generated `.labb/labb.css`, which your `input.css` pulls in with one line: `@import "../.labb/labb.css";`.

#### Publishing groups (`labb-provides.yaml`)

A package publishes its groups from a `labb-provides.yaml` at its root (see the [full reference]({% doc_url '5_references/5_labb_provides.md' 'guide' %}) and the [Developing packages]({% doc_url '4_going_further/2_developing_packages.md' 'guide' %}) guide):

```yaml
provides:
  themes:     { imports: [css/themes.css] }
  components: { components: [templates/cotton/lb/**/*.html], literals: [templates/cotton/lb/**/*.html] }
  blocks:     { components: [templates/cotton/lbb/**/*.html], literals: [templates/cotton/lbb/**/*.html] }
```

### CSS scan configuration

`css.scan.templates` lists **your own** template patterns, scanned for `<c-lb.*>` usage:

```yaml
css:
  scan:
    templates:
      - templates/**/*.html
      - '*/templates/**/*.html'
      - '**/templates/**/*.html'
```

<c-lb.alert variant="warning" alertStyle="outline" class="my-4">
  <span>`css.scan.apps` and `css.scan.output` are **deprecated** and replaced by `css.packages` (the safelist now lives in `.labb/`). Run <code>labb migrate</code> to convert an old config. See <a href="{% doc_url '6_about/3_migrating_to_0_5.md' 'guide' %}">Migrating to 0.5</a>.</span>
</c-lb.alert>

## Environment variables

By default, the labb CLI looks for `labb.yaml` or `labb.yml` files in the current working directory. You can override the configuration file location using environment variables:

- `LABB_CONFIG_PATH`: Override the configuration file location

**Default behavior:**
```bash
# CLI searches for these files in order:
# 1. labb.yaml
# 2. labb.yml
labb build
```

**Override with environment variable:**
```bash
export LABB_CONFIG_PATH=/path/to/custom.yaml
labb build
```

## Template patterns

The `css.scan.templates` array supports glob patterns to find template files:

```yaml
css:
  scan:
    templates:
      - templates/**/*.html          # Project templates
      - '*/templates/**/*.html'      # App templates
      - '**/templates/**/*.html'     # Nested app templates
      - components/**/*.html         # Component templates
      - 'myapp/custom/**/*.html'     # Specific app patterns
```

## Managing configuration

### Configuration validation

You can validate your configuration using the CLI:

```bash
# Validate configuration
labb config --validate

# Show configuration with metadata
labb config --metadata
```

### View current configuration

```bash
# Display current configuration
labb config

# Show with metadata
labb config --metadata
```

### Edit configuration

```bash
# Open configuration file in editor
labb config --edit
```

### Use custom configuration file

```bash
# Use specific config file
labb config --config /path/to/custom.yaml

# Set via environment variable
export LABB_CONFIG_PATH=/path/to/custom.yaml
labb build
```

## Reference

| Section | Option | Type | Default | Description |
|---------|--------|------|---------|-------------|
| `css.build.input` | string | `static_src/input.css` | Input CSS file path |
| `css.build.output` | string | `static/css/output.css` | Output CSS file path |
| `css.build.minify` | boolean | `true` | Whether to minify CSS output |
| `css.scan.output` | string | `static_src/labb-classes.txt` | Classes extraction output file |
| `css.scan.templates` | array | `["templates/**/*.html", ...]` | Template file patterns to scan |
| `css.scan.apps` | object | `{}` | Django apps to scan with optional app-specific patterns |
