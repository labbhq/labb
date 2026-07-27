---
doc_layout: component
component: c-lb.chart.bar
title: Bar Chart
description: "Compare values across categories in a Django template. Vertical bar charts drawn by Chart.js, coloured from the daisyUI palette, wired up with one django-cotton tag."
keywords: "django bar chart, bar chart django, chart.js django, daisyui chart django, tailwind chart django, django data visualization, bar chart django-cotton, django analytics"
daisy_ui_component_name: ""
icon: rmx.bar-chart
---

Reach for a bar chart when you are comparing values across categories: revenue by month, signups by source, requests by endpoint. Pass labels and datasets as JSON and each series picks up a daisyUI palette colour unless you name one yourself. Datasets can also override the chart type individually, which is how the combo examples below plot a target line over the bars.

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
