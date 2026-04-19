---
title: "Reactivity"
description: "Alpine.js reactivity in labb Django components: use `.x` variants for runtime props; no JS by default. django-cotton, Tailwind CSS, and daisyUI 5 compatible."
keywords: "labb alpine.js django, django reactivity, django-cotton alpine, labb .x component, server-side rendering django"
---

{% load docs_tags %}

labb is zero-JS by default, but components are integrated with [Alpine.js](https://alpinejs.dev/) to provide reactivity. This is available through the `.x` twin of each component, letting you change visual props at runtime without a page reload. Alpine is only loaded on pages where a `.x` component is used.

## The `.x` variant

Every reactive-capable component has an `.x` version. For example, `<c-lb.button.x>` is the reactive twin of `<c-lb.button>`. Drop it in as a replacement. The server still renders the initial HTML, and Alpine takes over from there:

```html
<!-- Before: plain server-rendered button -->
<c-lb.button variant="primary" size="lg">Save</c-lb.button>

<!-- After: same output, but now Alpine-powered -->
<c-lb.button.x variant="primary" size="lg">Save</c-lb.button.x>
```

## Usage

### Initial props

Pass props as HTML attributes on the `.x` component, the same as the regular version. They seed the initial server render and are also read by Alpine as the starting state:

<c-lbdocs.component_example path="button/reactive-initial" style="inline" />

### Changing props at runtime

To change props at runtime, bind an object containing props to the `.x` component using `x-model`.  The object can live anywhere Alpine can see it: inline `x-data`, a registered `Alpine.data` component, or any ancestor scope.

<c-lb.alert variant="info" alertStyle="outline" class="text-sm mb-6">
 <span> Not every prop can be changed reactively. In the API table, reactive props are marked with a <c-lbi n="rmx.flashlight" w="0.85em" h="0.85em" class="text-warning inline align-middle" /> icon.</span>
</c-lb.alert>

<c-lbdocs.component_example path="button/reactive-simple" style="stacked" />


### Adding your own behavior

When you need the component to do more than just swap classes (custom state, async actions, event handling), use `lb.extendComponent` to build on top of the built-in Alpine component rather than replace it. Your code gets added alongside the class management logic, so both work together.

Inside your methods, use `this.lbProps` to read or change the component's reactive props:

```js
this.lbProps.variant = 'success';
this.lbProps.size = 'lg';
```

<c-lbdocs.component_example path="button/reactive-extend" style="stacked" />

Initial props from HTML attributes are still seeded automatically. If you need a custom `init()`, call the base to keep that:

```js
Alpine.data('myBtnComp', lb.extendComponent('button', {
    init() {
        Object.getPrototypeOf(this).init?.call(this);
        // your custom init...
    }
}));
```

See the [`window.lb` reference]({% doc_url '3_references/5_window_lb.md' 'guide' %}) for full `lb.extendComponent` documentation.

### Replacing the Alpine component

You can also pass your own `x-data` entirely, which bypasses the built-in component:

```html
<c-lb.button.x x-data="{ myCustomSetup() { ... } }" variant="primary">
    Custom Alpine
</c-lb.button.x>
```

When you do this, the built-in class management no longer applies. You are responsible for handling reactive classes yourself.

## Prop format

Reactive props are plain JavaScript object keys matching the **camelCase variable names** from the API table. These are the same keys used in `lbProps` when extending:

```js
{
    variant: 'primary',   // btn-primary
    size: 'lg',           // btn-lg
    btnStyle: 'outline',  // btn-outline
    behavior: '',         // '' = no class applied
}
```

An empty string means "no value". Use it to clear a prop back to its unstyled state. You only need to include the props you want to control; the rest stay at their server-rendered defaults.


## Overriding the Alpine.js source

By default, labb serves Alpine from its own bundled static file. To use a CDN or your own build, set `ALPINE_JS_PATH` in your Django settings. See the [Django settings reference]({% doc_url '3_references/2_django_settings.md' 'guide' %}#alpine_js_path) for details.
