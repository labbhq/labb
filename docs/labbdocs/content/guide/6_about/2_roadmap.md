---
title: Roadmap
description: "labb roadmap: planned django ui components, tooling, and docs for the django component library toward v1."
keywords: "labb roadmap, django ui roadmap, labb future features"
doc_show_toc: false
---

## Roadmap to v1.0.0


Priorities may shift based on community feedback. Have a feature request? Open a discussion on [GitHub](https://github.com/labbhq/labb/discussions).


<div class="not-prose">
<c-lb.timeline direction="vertical" snap compact>
    <c-lb.timeline.item first variant="success" icon="rmx.checkbox-circle">
        <c-slot name="endSlot">
            <c-lb.timeline.end box class="my-6">
                <span class="font-bold">v0.3.0</span>
                <p class="text-sm">Full daisyUI components support</p>
            </c-lb.timeline.end>
        </c-slot>
    </c-lb.timeline.item>
    <c-lb.timeline.item variant="success" icon="rmx.checkbox-circle">
        <c-slot name="endSlot">
            <c-lb.timeline.end box class="my-6">
                <span class="font-bold">v0.4.0</span>
                <p class="text-sm">AlpineJS integration and Charts</p>
            </c-lb.timeline.end>
        </c-slot>
    </c-lb.timeline.item>
    <c-lb.timeline.item variant="success" icon="rmx.checkbox-circle">
        <c-slot name="endSlot">
            <c-lb.timeline.end box class="my-6">
                <span class="font-bold">v0.5.0</span>
                <p class="text-sm">Fullstack reactivity powered by Datastar, installable blocks, and package extendability</p>
            </c-lb.timeline.end>
        </c-slot>
    </c-lb.timeline.item>
    <c-lb.timeline.item icon="rmx.time">
        <c-slot name="endSlot">
            <c-lb.timeline.end box class="my-6">
                <span class="font-bold">Package component schemas</span>
                <p class="text-sm">Third-party packages declare their own component schemas, so labb scan resolves variant classes for their tags too</p>
            </c-lb.timeline.end>
        </c-slot>
    </c-lb.timeline.item>
    <c-lb.timeline.item icon="rmx.time">
        <c-slot name="endSlot">
            <c-lb.timeline.end box class="my-6">
                <span class="font-bold">More icon packs</span>
                <p class="text-sm">Additional icon libraries beyond Remix Icons</p>
            </c-lb.timeline.end>
        </c-slot>
    </c-lb.timeline.item>
    <c-lb.timeline.item icon="rmx.time">
        <c-slot name="endSlot">
            <c-lb.timeline.end box class="my-6">
                <span class="font-bold">Advanced components</span>
                <p class="text-sm">Date pickers, calendars, rich text editors, file upload, forms</p>
            </c-lb.timeline.end>
        </c-slot>
    </c-lb.timeline.item>
    <c-lb.timeline.item icon="rmx.time">
        <c-slot name="endSlot">
            <c-lb.timeline.end box class="my-6">
                <span class="font-bold">IDE extensions</span>
                <p class="text-sm">Autocomplete and inline documentation</p>
            </c-lb.timeline.end>
        </c-slot>
    </c-lb.timeline.item>
    <c-lb.timeline.item icon="rmx.time" last>
        <c-slot name="endSlot">
            <c-lb.timeline.end box class="my-6">
                <span class="font-bold">Starter kits</span>
                <p class="text-sm">Pre-built project templates for common use cases</p>
            </c-lb.timeline.end>
        </c-slot>
    </c-lb.timeline.item>
</c-lb.timeline>
</div>
