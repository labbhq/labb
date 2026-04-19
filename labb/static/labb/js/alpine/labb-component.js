window.lb = window.lb || {
  _registry: {},
  extendComponent(name, overrides) {
    const factory = this._registry[name];
    if (!factory) {
      const available = Object.keys(this._registry).join(', ');
      throw new Error(`[labb] Component "${name}" not found. Available: ${available}`);
    }
    return factory.extend(overrides);
  }
};

function createLabbComponent(config, componentName, publicName) {
  const allClasses = [
    ...config.baseClasses,
    ...Object.values(config.variables).flatMap(v => v.css_mapping ? Object.values(v.css_mapping) : [])
  ].filter(Boolean);

  const defaults = Object.fromEntries(
    Object.entries(config.variables).map(([k, s]) => [k, s.default ?? ''])
  );

  const factory = () => ({
    lbProps: { ...defaults },
    _attrDefaults: {},
    init() {
      const el = this.$el || this.$root;
      el.classList.remove(...allClasses);
      const raw = el.getAttribute('data-lb-defaults');
      if (raw) {
        this._attrDefaults = JSON.parse(raw);
        this.lbProps = { ...this.lbProps, ...this._attrDefaults };
      }
    },
    get fullCompProps() {
      return { ...defaults, ...this._attrDefaults, ...this.lbProps };
    },
    get compClasses() {
      return [
        ...config.baseClasses,
        ...Object.entries(this.fullCompProps)
          .map(([p, v]) => v && config.variables[p]?.css_mapping?.[String(v)])
          .filter(Boolean)
      ].join(' ');
    }
  });

  factory.extend = (overrides) => () => {
    const base = Object.defineProperties({}, Object.getOwnPropertyDescriptors(factory()));
    return Object.assign(base, overrides);
  };

  document.addEventListener('alpine:init', () => Alpine.data(componentName, factory));
  window[componentName] = factory;
  if (publicName) window.lb._registry[publicName] = factory;
}

window.lb.createComponent = createLabbComponent;
