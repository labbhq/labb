// collapse.js

const collapseConfig = {
  baseClasses: ["collapse"],
  variables: {
    style: {
        "default": "",
        "css_mapping": {
            "arrow": "collapse-arrow",
            "plus": "collapse-plus"
        }
    },
    open: {
        "default": false,
        "css_mapping": {
            "true": "collapse-open"
        }
    },
  }
};

window.lb.createComponent(collapseConfig, 'lbCollapseComp', 'collapse');
