---
title: llms.txt
description: Using labb with LLMs
doc_links:
    - title: llms.txt
      url: /llms.txt
      type: external
      icon: rmx.file_text
---

labb's `llms.txt` file can be accessed via the web or the `labb` CLI. *MCP server support coming soon.*

**Note:** All documentation pages can be accessed in raw markdown format by adding `.md` to the URL.

## Access Methods

### Web Access

<c-lb.button as="a" href="{% url 'llms_txt' %}" size="xs">
  <c-lbi.rmx.file_text w="1em" h="1em" />
  View llms.txt
</c-lb.button>

The `llms.txt` content is available via HTTP endpoint:

```bash
# Access via web browser or HTTP client
curl {{ llms_txt_url }}
```

**URL:** `{{ llms_txt_url }}`

### CLI Access

<c-lbdocs.misc.copy_button text="labb llms" label="labb llms" elementId="llms" icon="rmx.terminal" />

Use the `labb llms` command to display the content:

```bash
# Display complete llms.txt content
labb llms

# Pipe to other tools for processing
labb llms | grep "button"

# Search for specific components
labb llms | grep -A 10 "badge:"
```

### MCP Server
 *Coming soon*

## Editor Integration

### VSCode

**Quick Use**

In the VSCode chat window, type this and VSCode will use labb's llms.txt file to generate code:

```
#fetch {{ llms_txt_url }}
```

**Project-level Permanent Setup**

You can set up labb's llms.txt file in your workspace so Copilot can use it by default.

Run this command to save the llms.txt file to `.github/labb.instructions.md`:

```bash
curl -L {{ llms_txt_url }} --create-dirs -o .github/labb.instructions.md
```

### Cursor

**Quick Use**

In the Cursor chat window:

```
@web {{ llms_txt_url }}
```

**Permanent Setup**

1. Press `⌘ CMD+⇧ Shift+P` (or `⌃ Ctrl+⇧ Shift+P` on Windows)
2. Type `Add new custom docs`
3. Add this URL: `{{ llms_txt_url }}`
4. Now in the chat window, you can type `@docs` and choose `labb` to provide labb docs to Cursor

**Project-level Setup**

Run this command to save the llms.txt file to `.cursor/rules/labb.mdc`:

```bash
curl -L {{ llms_txt_url }} --create-dirs -o .cursor/rules/labb.mdc
```

### Zed

**Quick Use**

In Zed's chat window, type this to use labb's llms.txt file:

```
@web {{ llms_txt_url }}
```

**Project-level Setup**

Run this command to save the llms.txt file to `.zed/rules/labb.mdc`:

```bash
curl -L {{ llms_txt_url }} --create-dirs -o .zed/rules/labb.mdc
```

### Windsurf

**Quick Use**

In Windsurf's chat window, type this to use labb's llms.txt file:

```
@web {{ llms_txt_url }}
```

**Project-level Setup**

Run this command to save the llms.txt file to `.windsurf/rules/labb.mdc`:

```bash
curl -L {{ llms_txt_url }} --create-dirs -o .windsurf/rules/labb.mdc
```

### ChatGPT

**Quick Use**

Enable `🌐 Search` feature and add this before your prompt:

```
{{ llms_txt_url }}
```

**Example:**

```
{{ llms_txt_url }} give me a labb button component with primary variant
```

### Gemini

**Quick Use**

Enable `🔍 Deep research` feature and add this before your prompt:

```
{{ llms_txt_url }}
```

**Example:**

```
{{ llms_txt_url }} create a labb card component with image and description
```

### Grok

**Quick Use (Deep Search)**

Enable `꩜ Deep Search` feature and add this before your prompt:

```
{{ llms_txt_url }}
```

**Workspace Setup (SuperGrok Only)**

1. Visit `{{ llms_txt_url }}`
2. Right-click and select "Save As..." to download the file
3. Upload as attachment in Grok Workspace
4. All conversations in this workspace will have access to labb docs

### Cline

**Quick Use**

In Cline's chat window, type this to use labb's llms.txt file:

```
@web {{ llms_txt_url }}
```

**Project-level Setup**

Run this command to save the llms.txt file to `.cline/rules/labb.mdc`:

```bash
curl -L {{ llms_txt_url }} --create-dirs -o .cline/rules/labb.mdc
```
