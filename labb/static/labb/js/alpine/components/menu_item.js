// menu_item.js

const menuItemConfig = {
  baseClasses: [],
  variables: {
    type: {
        "default": "link",
        "css_mapping": {
            "title": "menu-title",
            "submenu-details": "menu-dropdown",
            "submenu-toggle": "menu-dropdown-toggle"
        }
    },
    size: {
        "default": "",
        "css_mapping": {
            "xs": "menu-xs",
            "sm": "menu-sm",
            "md": "menu-md",
            "lg": "menu-lg",
            "xl": "menu-xl"
        }
    },
    disabled: {
        "default": false,
        "css_mapping": {
            "true": "menu-disabled"
        }
    },
    active: {
        "default": false,
        "css_mapping": {
            "true": "menu-active"
        }
    },
    open: {
        "default": false,
        "css_mapping": {
            "true": "menu-dropdown-show"
        }
    },
  }
};

window.lb.createComponent(menuItemConfig, 'lbMenuItemComp', 'menu.item');
