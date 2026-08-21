---
doc_layout: component
component: c-lb.countdown
title: Countdown
description: "Countdown component for Django: animate a rolling number for timers, clocks, and counters. Built with django-cotton, Tailwind CSS, and daisyUI 5."
keywords: "django countdown component, countdown timer django, daisyui countdown django, tailwind countdown django, countdown django-cotton, django ui timer, clock django, django-cotton"
daisy_ui_component_name: countdown
icon: rmx.timer
---

Countdown renders a single number (0–999) that rolls smoothly when it changes. The roll is pure CSS; something has to change the value. Bind `value` to a signal and it counts on its own. With a static value it renders one number and ships no JavaScript.

Compose several to build a clock, and set the type size with a `class`.

## Basic Countdown
<c-lbdocs.component_example path="countdown/basic" />

## Counting down
Bind `value` to a signal and drive it from an interval. The `:10` after the signal name is the server-rendered fallback.

<c-lbdocs.component_example path="countdown/ticking" />

## Clock
Static digits. Renders once, no JavaScript.

<c-lbdocs.component_example path="countdown/clock" />

## Reactive clock
The same composition with each unit bound to its own signal. Use `digits="2"` to reserve a fixed width so the row does not jump as numbers change.

<c-lbdocs.component_example path="countdown/reactive-clock" />

## With Labels
<c-lbdocs.component_example path="countdown/with-labels" />

## API Reference
### `c-lb.countdown`
<c-lbdocs.api_table component_name="countdown" />
