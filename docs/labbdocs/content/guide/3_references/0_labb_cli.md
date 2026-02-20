---
title: labb CLI
description: Complete reference for the labb command-line interface
---

The `labb` command-line interface provides a comprehensive set of tools for managing your Django projects using labb.



## Commands Overview

| Command | Description |
|---------|-------------|
| `init` | Initialize labb project with configuration and project structure |
| `setup` | Install labb dependencies (Tailwind CSS CLI and daisyUI) |
| `scan` | Scan templates for labb components |
| `build` | Build CSS using Tailwind CSS 4 |
| `dev` | Development mode with watch and scan |
| `config` | Display, validate, or edit configuration |
| `icons` | Search and manage icon packs (requires labbicons package) |
| `components` | Inspect available components and view their examples |
| `llms` | Display llms.txt content for AI/LLM consumption |

## Reference

### `labb init`

<c-lbdocs.indented_block>
Initialize a new labb project with configuration and project structure.

**Usage:**
```bash
labb init [OPTIONS]
```

**Options:**

- `--defaults`: Use default values without prompts
- `--force`: Overwrite existing files and directories created by `labb init`

**Examples:**
```bash
# Interactive initialization
labb init

# Use defaults for quick setup
labb init --defaults

# Force overwrite existing files
labb init --force
```

</c-lbdocs.indented_block>

### `labb setup`

<c-lbdocs.indented_block>
Install labb dependencies (Tailwind CSS CLI and daisyUI) in the current Django project.

**Usage:**
```bash
labb setup [OPTIONS]
```

**Options:**

- `--install-deps / --no-install-deps`: Install Node.js dependencies

**Examples:**
```bash
# Install dependencies (interactive)
labb setup

# Install dependencies automatically
labb setup --install-deps

# Skip dependency installation
labb setup --no-install-deps
```

</c-lbdocs.indented_block>


### `labb scan`

<c-lbdocs.indented_block>
Scan templates for labb components and extract CSS classes.

**Usage:**
```bash
labb scan [OPTIONS]
```

**Options:**

- `--watch, -w`: Watch for changes and rescan
- `--output, -o TEXT`: Override output file path
- `--patterns TEXT`: Override template patterns (comma-separated)
- `--verbose, -v`: Show detailed scanning information

**Examples:**
```bash
# Scan templates once
labb scan

# Watch for changes
labb scan --watch

# Custom output file
labb scan --output src/extracted-classes.txt

# Custom template patterns
labb scan --patterns "templates/**/*.html,components/**/*.html"

# Verbose output
labb scan --verbose
```

</c-lbdocs.indented_block>


### `labb build`

<c-lbdocs.indented_block>
Build CSS using Tailwind CSS 4 with labb configuration.

**Usage:**
```bash
labb build [OPTIONS]
```

**Options:**

- `--watch, -w`: Watch for changes and rebuild
- `--scan, -s`: Scan templates for CSS classes (behavior depends on watch mode)
- `--minify / --no-minify`: Minify CSS output (default: from config)
- `--input, -i TEXT`: Override input CSS file path
- `--output, -o TEXT`: Override output CSS file path

**Examples:**
```bash
# One-time build
labb build

# Watch for changes
labb build --watch

# Scan templates before building
labb build --scan

# Development mode (concurrent watch + scan)
labb build --watch --scan

# Override minification
labb build --no-minify

# Custom input/output files
labb build --input src/styles.css --output dist/app.css
```

</c-lbdocs.indented_block>

### `labb dev`

<c-lbdocs.indented_block>
Development mode: watch and build CSS + scan templates concurrently.

**Usage:**
```bash
labb dev [OPTIONS]
```

**Options:**

- `--minify / --no-minify`: Minify CSS output (default: false for dev)
- `--input, -i TEXT`: Override input CSS file path
- `--output, -o TEXT`: Override output CSS file path

**Examples:**
```bash
# Start development mode
labb dev

# Development mode with minification
labb dev --minify

# Custom file paths
labb dev --input src/styles.css --output dist/app.css
```

</c-lbdocs.indented_block>

### `labb config`

<c-lbdocs.indented_block>
Display, validate, or edit labb configuration in YAML format.

**Usage:**
```bash
labb config [OPTIONS]
```

**Options:**

- `--metadata, -m`: Show configuration metadata
- `--validate, -v`: Validate configuration and check files
- `--edit, -e`: Open configuration file in editor
- `--config, -c TEXT`: Path to specific configuration file

**Examples:**
```bash
# Show current configuration
labb config

# Show with metadata
labb config --metadata

# Validate configuration
labb config --validate

# Edit configuration file
labb config --edit

# Use specific config file
labb config --config /path/to/custom.yaml
```

</c-lbdocs.indented_block>


### `labb components`

<c-lbdocs.indented_block>
Inspect available components and view their examples.

**Usage:**
```bash
labb components [SUBCOMMAND] [OPTIONS]
```

**Subcommands:**

- `inspect`: Inspect component specifications
- `ex`: View component examples

#### `labb components inspect`

<c-lbdocs.indented_block>

Inspect available components and their specifications.

**Usage:**
```bash
labb components inspect [OPTIONS] [COMPONENT]
```

**Arguments:**

- `COMPONENT`: Specific component to inspect

**Options:**

- `--list, -l`: List all components
- `--verbose, -v`: Show detailed information (includes raw YAML)

**Examples:**
```bash
# List all components
labb components inspect

# List with details
labb components inspect --list --verbose

# Inspect specific component
labb components inspect button

# Detailed component inspection with raw YAML
labb components inspect button --verbose
```

</c-lbdocs.indented_block>

#### `labb components ex`

<c-lbdocs.indented_block>

View and explore component examples.

**Usage:**
```bash
labb components ex [OPTIONS] [COMPONENT] [EXAMPLES]...
```

**Arguments:**

- `COMPONENT`: Component name to show examples for
- `EXAMPLES`: Specific example(s) to display (can specify multiple)

**Options:**

- `--list, -l`: List all components with examples
- `--tree, -t`: Show examples in tree format

**Examples:**
```bash
# List all components with examples
labb components ex --list

# Show examples tree view
labb components ex --tree

# List examples for a specific component
labb components ex badge

# View a specific example
labb components ex badge basic

# View multiple examples at once
labb components ex badge basic color-variants sizes

# View examples from different components
labb components ex button primary-button
labb components ex modal basic-modal
```

</c-lbdocs.indented_block></c-lbdocs.indented_block>

### `labb icons`

<c-lbdocs.indented_block>
Search and manage icon packs (requires <a href="{% doc_url '1_getting_started/2_installation.md' 'icons' %}">labbicons package</a> to be installed).

> *If the `labbicons` package is not installed, the command will show an error with installation instructions.*

**Usage:**
```bash
labb icons [SUBCOMMAND] [OPTIONS]
```

**Subcommands:**

- `search`: Search for icons by name, pack, category, or variant
- `packs`: List all available icon packs with categories
- `info`: Show detailed information about a specific icon

#### `labb icons search`

<c-lbdocs.indented_block>
Search for icons by name, pack, category, or variant.

**Usage:**
```bash
labb icons search QUERY [OPTIONS]
```

**Arguments:**

- `QUERY`: Search term for icon names

**Options:**

- `--pack, -p TEXT`: Filter by icon pack (e.g., rmx)
- `--category, -c TEXT`: Filter by category
- `--variant, -v TEXT`: Filter by variant (fill, line)
- `--limit, -l INTEGER`: Maximum number of results to show (default: 20)

**Examples:**
```bash
# Search for icons containing "arrow"
labb icons search "arrow"

# Search in specific pack
labb icons search "arrow" --pack rmx

# Search by category
labb icons search "arrow" --category Arrows

# Search with variant filter
labb icons search "arrow" --variant fill

# Limit results
labb icons search "arrow" --limit 5
```

</c-lbdocs.indented_block>

#### `labb icons packs`

<c-lbdocs.indented_block>
List all available icon packs with categories and counts.

**Usage:**
```bash
labb icons packs
```

**Examples:**
```bash
# List all available packs
labb icons packs
```

</c-lbdocs.indented_block>

#### `labb icons info`

<c-lbdocs.indented_block>
Show detailed information about a specific icon using pack.icon format.

**Usage:**
```bash
labb icons info ICON_IDENTIFIER
```

**Arguments:**

- `ICON_IDENTIFIER`: Icon identifier in format 'pack.icon' (e.g., 'rmx.arrow-down')

**Examples:**
```bash
# Get detailed info about an icon
labb icons info rmx.arrow-down

# Get info about another icon
labb icons info rmx.home
```
</c-lbdocs.indented_block>

</c-lbdocs.indented_block>

### `labb llms`

<c-lbdocs.indented_block>
Display llms.txt content for AI/LLM consumption.

**Usage:**
```bash
labb llms
```

**Examples:**
```bash
# Display complete llms.txt content
labb llms

# Pipe to other tools
labb llms | grep "variant:"

# Search for specific components
labb llms | grep "button"
```


</c-lbdocs.indented_block>


## Development Workflow

### 1. Project Initialization

```bash
# Initialize project (creates config + project structure)
labb init

# Install dependencies
labb setup
```

**For new developers joining an existing project:**
```bash
# Just install dependencies (project already initialized)
labb setup
```

### 2. Development

```bash
# Start development mode
labb dev
```

This runs both CSS building and template scanning in watch mode.

### 3. Production Build

```bash
# Build for production
labb build --minify
```

### 4. Component Usage

```bash
# List all components
labb components inspect --list

# Inspect specific component
labb components inspect button --verbose

# Explore component examples
labb components ex --tree

# View specific examples
labb components ex badge basic color-variants
```

### 5. Icon Usage (Optional)

```bash
# Install labbicons package first
pip install labbicons

# List available icon packs
labb icons packs

# Search for icons
labb icons search "arrow"

# Get detailed icon information
labb icons info rmx.arrow-down
```

## Troubleshooting

### Common Issues

**"npx is not available"**
```bash
# Install Node.js and npm
# Visit https://nodejs.org/
```

**"Configuration file not found"**
```bash
# Initialize project
labb init
```

**"package.json not found"**
```bash
# Initialize project first, then setup
labb init
labb setup
```

**"Input CSS file not found"**
```bash
# Initialize project (creates CSS files)
labb init
```

**"No template files found"**
```bash
# Check template patterns in labb.yaml
labb config --validate
```

### Getting Help

```bash
# Show general help
labb --help

# Show command-specific help
labb build --help
labb llms --help

# Show components help
labb components --help

# Show subcommand help
labb components inspect --help
labb components ex --help
```

## Advanced Usage

### Custom Configuration

```bash
# Use custom config file
export LABB_CONFIG_PATH=/path/to/custom.yaml
labb build

# Or specify directly
labb build --config /path/to/custom.yaml
```

### CI/CD Integration

```bash
# Non-interactive setup
labb init --defaults
labb setup --install-deps

# Production build
labb build --minify
```

### AI/LLM Integration

```bash
# Get complete documentation for AI consumption
labb llms

# Extract specific component information
labb llms | grep -A 10 "button:"

# Get installation instructions
labb llms | grep -A 5 "## Installation"
```
