// menu.js

const menuConfig = {
  baseClasses: ["menu"],
  variables: {
    direction: {
        "default": "vertical",
        "css_mapping": {
            "horizontal": "menu-horizontal"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "menu-xs",
            "sm": "menu-sm",
            "md": "menu-md",
            "lg": "menu-lg",
            "xl": "menu-xl"
        }
    },
  }
};

window.lb.createComponent(menuConfig, 'lbMenuComp', 'menu');
