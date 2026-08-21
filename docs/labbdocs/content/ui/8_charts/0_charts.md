---
doc_layout: component
component: c-lb.chart
title: Charts
description: "Chart.js charts for Django with labb: bar, line, pie, doughnut, radar, polar, scatter, and bubble. DaisyUI colours, django-cotton components, server-friendly defaults."
keywords: "django charts, chart.js django, django data visualization, daisyui charts django, django-cotton charts, labb chart"
daisy_ui_component_name: ""
icon: rmx.bar-chart-box
---

Eight chart types, from a plain bar chart to radar and bubble. Each one takes a JSON string from your view and renders through Chart.js in DaisyUI's colours, so a dashboard chart matches the page around it without a separate frontend build.

<c-lbdocs.component_example path="chart/bar" />

## Overview

labb wraps [Chart.js](https://www.chartjs.org/) with django-cotton components. Each chart type is a self-contained component that loads Chart.js, applies DaisyUI theming, and redraws automatically when the user switches theme.


## Chart types

| Component | Description |
|---|---|
| <a href="{% doc_url '8_charts/bar.md' 'ui' %}">`c-lb.chart.bar`</a> | Vertical bar chart |
| <a href="{% doc_url '8_charts/line.md' 'ui' %}">`c-lb.chart.line`</a> | Line chart with optional fill areas |
| <a href="{% doc_url '8_charts/pie.md' 'ui' %}">`c-lb.chart.pie`</a> | Pie chart |
| <a href="{% doc_url '8_charts/doughnut.md' 'ui' %}">`c-lb.chart.doughnut`</a> | Doughnut chart |
| <a href="{% doc_url '8_charts/radar.md' 'ui' %}">`c-lb.chart.radar`</a> | Radar / spider chart |
| <a href="{% doc_url '8_charts/polar_area.md' 'ui' %}">`c-lb.chart.polar-area`</a> | Polar area chart |
| <a href="{% doc_url '8_charts/scatter.md' 'ui' %}">`c-lb.chart.scatter`</a> | Scatter plot with {x, y} point objects |
| <a href="{% doc_url '8_charts/bubble.md' 'ui' %}">`c-lb.chart.bubble`</a> | Bubble chart with {x, y, r} point objects |

`<c-lb.chart />` is optional. Use it when you want to set global defaults (grid lines, animations, font size, etc.) that apply to every chart on the page. Without it, charts render with labb's own defaults.

## Setup

Drop any chart component into your template and pass a JSON data string:

```html
<c-lb.chart.bar data='{
    "labels": ["Jan", "Feb", "Mar"],
    "datasets": [{"label": "Revenue", "data": [120, 190, 150]}]
}' />
```

To share global defaults across all charts on a page, place `<c-lb.chart />` once in your base template:

```html
{# base.html, optional, for global defaults #}
<c-lb.chart grid animation="False" />

{# any page #}
<c-lb.chart.bar data="..." />
<c-lb.chart.line data="..." />
```

## Passing data from Django

Serialise your data with `json.dumps` in the view, then bind it with `:data`:

```python
# views.py
import json

context["chart_data"] = json.dumps({
    "labels": ["Jan", "Feb", "Mar"],
    "datasets": [{"label": "Revenue", "data": [120, 190, 150]}],
})
```

```html
<c-lb.chart.bar :data='chart_data' />
```

## Colour system

Datasets without an explicit `backgroundColor` are automatically coloured from the DaisyUI palette, cycling through: `primary`, `secondary`, `accent`, `info`, `success`, `warning`, `error`.

You can use semantic DaisyUI colour names directly in your dataset JSON:

```json
{
  "datasets": [
    { "label": "Revenue",  "backgroundColor": "primary" },
    { "label": "Expenses", "backgroundColor": "error", "borderColor": "error" }
  ]
}
```

Supported names: `primary`, `secondary`, `accent`, `neutral`, `info`, `success`, `warning`, `error`, plus `-content` variants (e.g. `primary-content`). CSS variable names (e.g. `--color-primary`) also work.

Charts automatically redraw when the user switches DaisyUI theme.

## Dynamic data

For charts that update at runtime (live feeds, interactive dashboards, user-driven filters), bind the chart to a signal: declare the data on `<c-lbr.signals>` and pass it to the chart as `data="$chartData"`. Mutating the signal redraws the chart in place, with no page reload, and labb's theming still applies automatically.

<c-lbdocs.component_example path="chart/bar-update" />

## Overriding Chart.defaults

For anything beyond the props on `c-lb.chart`, set `Chart.defaults` directly in a `<script>` tag after `<c-lb.chart />`. Your overrides layer on top of labb's defaults and persist across theme changes.

```html
<c-lb.chart />
<script>
    document.addEventListener('DOMContentLoaded', function () {
        Chart.defaults.plugins.tooltip.titleFont = { size: 13, weight: 'bold' };
        Chart.defaults.plugins.tooltip.bodyFont  = { size: 12 };
        Chart.defaults.scales.linear.grid.lineWidth = 0.5;
        Chart.defaults.elements.point.radius = 0;
        Chart.defaults.elements.point.hitRadius = 10;
    });
</script>
```

All available properties are documented in the [Chart.js configuration reference](https://www.chartjs.org/docs/latest/configuration/).

## API Reference

### `c-lb.chart`
<c-lbdocs.api_table component_name="chart" />
