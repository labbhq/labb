---
doc_layout: component
component: c-lb.chart.scatter
title: Scatter Chart
description: "Plot X/Y points in a Django template to look for correlation or spread. Chart.js scatter plots with daisyUI theming, dropped in as a django-cotton component."
keywords: "django scatter chart, scatter plot django, chart.js django, daisyui scatter chart django, tailwind chart django, django data visualization, scatter plot django-cotton"
daisy_ui_component_name: ""
icon: rmx.area-chart
---

Use a scatter chart when the shape of the cloud is the point: correlation, clustering, outliers. The dataset array holds one `{x, y}` object per point rather than a flat list of numbers.

## Basic Scatter Chart
<c-lbdocs.component_example path="chart/scatter" />

## Combo: Scatter + Trend Line
Add a `type: "line"` dataset with two endpoint `{x, y}` objects to overlay a trend line. Set `pointRadius: 0` and `borderDash` to style it as a reference rather than a data series.
<c-lbdocs.component_example path="chart/scatter-line" />

## API Reference
<c-lbdocs.api_table component_name="chart.scatter" />
