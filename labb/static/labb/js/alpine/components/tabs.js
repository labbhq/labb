// tabs.js

const tabsConfig = {
  baseClasses: ["tabs"],
  variables: {
    style: {
        "default": "",
        "css_mapping": {
            "border": "tabs-border",
            "lift": "tabs-lift",
            "box": "tabs-box"
        }
    },
    placement: {
        "default": "top",
        "css_mapping": {
            "bottom": "tabs-bottom"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "tabs-xs",
            "sm": "tabs-sm",
            "md": "tabs-md",
            "lg": "tabs-lg",
            "xl": "tabs-xl"
        }
    },
  }
};

window.lb.createComponent(tabsConfig, 'lbTabsComp', 'tabs');
