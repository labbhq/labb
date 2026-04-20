// toggle.js

const toggleConfig = {
  baseClasses: ["toggle"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "primary": "toggle-primary",
            "secondary": "toggle-secondary",
            "accent": "toggle-accent",
            "neutral": "toggle-neutral",
            "info": "toggle-info",
            "success": "toggle-success",
            "warning": "toggle-warning",
            "error": "toggle-error"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "toggle-xs",
            "sm": "toggle-sm",
            "md": "toggle-md",
            "lg": "toggle-lg",
            "xl": "toggle-xl"
        }
    },
    checked: {
        "default": false,
        "css_mapping": {
            "true": "checked"
        }
    },
    disabled: {
        "default": false,
        "css_mapping": {
            "true": "disabled"
        }
    },
    validate: {
        "default": false,
        "css_mapping": {
            "true": "validator"
        }
    },
  }
};

window.lb.createComponent(toggleConfig, 'lbToggleComp', 'toggle');
