---
doc_layout: component
component: c-lb.chart.bar
title: Bar Chart
description: "Bar chart component for Django: render vertical bar charts with Chart.js, daisyUI theming, and automatic colour palettes. Server-rendered with django-cotton."
keywords: "django bar chart, bar chart django, chart.js django, daisyui chart django, tailwind chart django, django data visualization, bar chart django-cotton, django analytics"
daisy_ui_component_name: ""
---

Bar chart for Django lets you render vertical bar charts using Chart.js with automatic
daisyUI colour palette integration. Built on django-cotton, it is fully server-rendered:
pass your data as JSON from any Django view and the chart is ready. Use it to visualise
comparisons, analytics, and multi-dataset metrics in Django dashboards.

## Basic Bar Chart
<c-lbdocs.component_example path="chart/bar" />

## Multiple Datasets Bar Chart
<c-lbdocs.component_example path="chart/bar-multi" />

## Semantic Colour Variants Bar Chart
<c-lbdocs.component_example path="chart/bar-colours" />

## Reactive Bar Chart
<c-lbdocs.component_example path="chart/bar-update" />

## Combo: Bar Chart + Target Line
Mix chart types per-dataset using the `type` key. Any dataset can override the base chart type.
<c-lbdocs.component_example path="chart/bar-line" />

## Combo: Dual Y-Axis Bar Chart
Use `yAxisID` on each dataset and configure two scales in `options` to plot datasets with different units side-by-side.
<c-lbdocs.component_example path="chart/bar-line-dual-axis" />

## API Reference
<c-lbdocs.api_table component_name="chart.bar" />
