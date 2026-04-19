// select.js

const selectConfig = {
  baseClasses: ["select"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "select-neutral",
            "primary": "select-primary",
            "secondary": "select-secondary",
            "accent": "select-accent",
            "info": "select-info",
            "success": "select-success",
            "warning": "select-warning",
            "error": "select-error"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "select-xs",
            "sm": "select-sm",
            "md": "select-md",
            "lg": "select-lg",
            "xl": "select-xl"
        }
    },
    ghost: {
        "default": false,
        "css_mapping": {
            "true": "select-ghost"
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

window.lb.createComponent(selectConfig, 'lbSelectComp', 'select');
