// drawer.js

const drawerConfig = {
  baseClasses: ["drawer", "drawer-toggle", "drawer-content"],
  variables: {
    end: {
        "default": false,
        "css_mapping": {
            "true": "drawer-end"
        }
    },
    open: {
        "default": false,
        "css_mapping": {
            "true": "drawer-open"
        }
    },
  }
};

window.lb.createComponent(drawerConfig, 'lbDrawerComp', 'drawer');
