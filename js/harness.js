// Loads a labb browser script into a throwaway context with the minimum DOM it
// touches, so the modules can be tested without a browser or a DOM library.

const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const JS_DIR = path.join(__dirname, '..', 'labb', 'static', 'labb', 'js');

class FakeClassList {
    constructor() { this._set = new Set(); }
    add(...v) { v.forEach((x) => this._set.add(x)); }
    remove(...v) { v.forEach((x) => this._set.delete(x)); }
    contains(v) { return this._set.has(v); }
}

class FakeElement {
    constructor(tag = 'div', dataset = {}) {
        this.tagName = tag.toUpperCase();
        this.dataset = dataset;
        this.children = [];
        this.classList = new FakeClassList();
        this.attributes = {};
        this.isConnected = true;
    }

    appendChild(child) { this.children.push(child); return child; }
    removeAttribute(name) { delete this.attributes[name]; }
    setAttribute(name, value) { this.attributes[name] = value; }

    querySelector(sel) {
        const tag = sel.toUpperCase();
        for (const child of this.children) {
            if (child.tagName === tag) return child;
            const found = child.querySelector ? child.querySelector(sel) : null;
            if (found) return found;
        }
        return null;
    }
}

// Records every Chart.js construction so tests can assert on the resolved config.
class FakeChart {
    constructor(canvas, config) {
        this.canvas = canvas;
        this.type = config.type;
        this.data = config.data;
        this.options = config.options;
        this.destroyed = false;
        this.updates = 0;
        FakeChart.built.push(this);
    }

    update() { this.updates += 1; }
    destroy() { this.destroyed = true; }

    static reset() { FakeChart.built = []; }
}
FakeChart.built = [];

function makeChartEl(dataset = {}) {
    const el = new FakeElement('div', dataset);
    el.appendChild(new FakeElement('canvas'));
    return el;
}

// Fresh context per test file, so module state never leaks between tests.
function loadScript(name) {
    const listeners = {};
    const observers = [];

    const documentElement = new FakeElement('html');
    const documentStub = {
        documentElement,
        addEventListener(type, fn) { (listeners[type] = listeners[type] || []).push(fn); },
        removeEventListener(type, fn) {
            const list = listeners[type] || [];
            const i = list.indexOf(fn);
            if (i !== -1) list.splice(i, 1);
        },
    };

    class FakeMutationObserver {
        constructor(cb) { this.cb = cb; this.disconnected = false; observers.push(this); }
        observe(target, opts) { this.target = target; this.opts = opts; }
        disconnect() { this.disconnected = true; }
    }

    const sandbox = {
        window: { Chart: FakeChart },
        document: documentStub,
        MutationObserver: FakeMutationObserver,
        JSON,
        console,
    };
    sandbox.globalThis = sandbox;

    const context = vm.createContext(sandbox);
    const code = fs.readFileSync(path.join(JS_DIR, name), 'utf8');
    vm.runInContext(code, context, { filename: name });

    return {
        window: sandbox.window,
        document: documentStub,
        observers,
        fire(type) { (listeners[type] || []).forEach((fn) => fn()); },
        listenerCount(type) { return (listeners[type] || []).length; },
        themeChange() { observers.forEach((o) => !o.disconnected && o.cb()); },
    };
}

module.exports = { loadScript, makeChartEl, FakeChart, FakeElement };
