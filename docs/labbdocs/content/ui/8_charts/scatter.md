---
doc_layout: component
component: c-lb.chart.scatter
title: Scatter Chart
description: "Scatter chart component for Django: plot X/Y data points with Chart.js and daisyUI theming. Server-rendered with django-cotton."
keywords: "django scatter chart, scatter plot django, chart.js django, daisyui scatter chart django, tailwind chart django, django data visualization, scatter plot django-cotton"
daisy_ui_component_name: ""
---

Scatter charts plot individual data points on X/Y axes, suited for correlation and distribution analysis. Each point is a `{x, y}` object in the dataset array.

## Basic Scatter Chart
<c-lbdocs.component_example path="chart/scatter" />

## Combo: Scatter + Trend Line
Add a `type: "line"` dataset with two endpoint `{x, y}` objects to overlay a trend line. Set `pointRadius: 0` and `borderDash` to style it as a reference rather than a data series.
<c-lbdocs.component_example path="chart/scatter-line" />

## API Reference
<c-lbdocs.api_table component_name="chart.scatter" />
