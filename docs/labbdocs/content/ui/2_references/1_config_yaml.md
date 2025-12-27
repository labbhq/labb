---
title: labb.yaml
description: Configuration options for your labb project
---

{% load docs_tags %}

The `labb.yaml` configuration file controls most aspects of your labb project. This file is created when you run `labb init` and is used by all labb CLI commands.

## Default Configuration

Here's the default structure of a `labb.yaml` file when you run `labb init`:

```yaml
css:
  build:
    input: static_src/input.css
    output: static/css/output.css
    minify: true
  scan:
    output: static_src/labb-classes.txt
    templates:
      - templates/**/*.html
      - '*/templates/**/*.html'
      - '**/templates/**/*.html'
```

## Configuration Sections

### CSS Build Configuration

Controls how CSS is built using Tailwind CSS 4 when using the <a href="{% doc_url '2_references/0_labb_cli.md' 'ui' %}#labb-build">`labb build`</a> command:

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

### CSS Scan Configuration

Controls how templates are scanned for labb components when using the <a href="{% doc_url '2_references/0_labb_cli.md' 'ui' %}#labb-scan">`labb scan`</a> command:

```yaml
css:
  scan:
    output: static_src/labb-classes.txt  # Classes extraction output file
    templates:                           # Template file patterns to scan
      - templates/**/*.html
      - '*/templates/**/*.html'
      - '**/templates/**/*.html'
    apps:                               # Django apps to scan with optional app-specific patterns
      myapp:                            # Another app (uses default patterns)
      myapp_with_patterns:              # App with custom patterns
        - templates/components/**/*.html  # Only component templates
        - templates/pages/**/*.html       # And page templates
        - ../glob/pattern/path/**/*.html
```

These settings can be overridden using command-line parameters:

```bash
# Override output file
labb scan --output src/extracted-classes.txt

# Override template patterns
labb scan --patterns "templates/**/*.html,components/**/*.html"

# Use watch mode (not in config)
labb scan --watch
```

## Environment Variables

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

## Template Patterns

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

## Managing Configuration

### Configuration Validation

You can validate your configuration using the CLI:

```bash
# Validate configuration
labb config --validate

# Show configuration with metadata
labb config --metadata
```

### View Current Configuration

```bash
# Display current configuration
labb config

# Show with metadata
labb config --metadata
```

### Edit Configuration

```bash
# Open configuration file in editor
labb config --edit
```

### Use Custom Configuration File

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
