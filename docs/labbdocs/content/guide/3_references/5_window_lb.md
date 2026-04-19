---
title: window.lb
description: "window.lb JavaScript API for Alpine.js-powered labb reactive components: bridge Django-rendered HTML and client-side state."
keywords: "window.lb, labb alpine.js, django alpine reactive components"
---

{% load docs_tags %}

## Overview

labb exposes a global `window.lb` object that serves as the namespace for its client-side Alpine.js integration. It is inlined automatically by `<c-lb.m.dependencies />` whenever a `.x` reactive component is on the page.

**Source:** [labb-component.js](https://github.com/labbhq/labb/blob/main/labb/static/labb/js/alpine/labb-component.js)

---

## Reference

### `lb.extendComponent(name, overrides)`

<c-lbdocs.indented_block>

Use this when you need a component to do more than just swap classes. Add your own state, methods, and logic while keeping the built-in reactive class management working. Register the result with `Alpine.data`, then pass the name to `x-data` on the `.x` component.

Inside your methods, `this.lbProps` gives you read/write access to the component's reactive props (variant, size, etc.). Changing a value immediately updates the component's classes.

**Parameters:**

- `name` *(string)* — the component to extend (e.g. `'button'`, `'stat.group'`)
- `overrides` *(object)* — your custom state and methods to add to the component

**Returns:** An Alpine data factory. Pass directly to `Alpine.data`.

**Throws:** If `name` is not a registered component, an error is thrown listing the available names.

**Example:**

```js
document.addEventListener('alpine:init', () => {
    Alpine.data('saveBtnComp', lb.extendComponent('button', {
        state: 'initial',
        async save() {
            this.lbProps.variant = 'info';
            this.state = 'saving';
            await fetch('/api/save');
            this.lbProps.variant = 'success';
            this.state = 'saved';
        },
    }));
});
```

```html
<c-lb.button.x x-data="saveBtnComp" variant="primary" @click="save()">
    Save
</c-lb.button.x>
```

If you need a custom `init()`, call the base to preserve automatic `lbProps` seeding from HTML attributes:

```js
lb.extendComponent('button', {
    init() {
        Object.getPrototypeOf(this).init?.call(this);
        // your custom init...
    }
})
```

Dot notation is supported for sub-components:

```js
lb.extendComponent('stat.group', { ... })
lb.extendComponent('validator.hint', { ... })
```

</c-lbdocs.indented_block>
