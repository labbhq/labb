// input.js

const inputConfig = {
  baseClasses: ["input"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "input-neutral",
            "primary": "input-primary",
            "secondary": "input-secondary",
            "accent": "input-accent",
            "info": "input-info",
            "success": "input-success",
            "warning": "input-warning",
            "error": "input-error"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "input-xs",
            "sm": "input-sm",
            "md": "input-md",
            "lg": "input-lg",
            "xl": "input-xl"
        }
    },
    ghost: {
        "default": false,
        "css_mapping": {
            "true": "input-ghost"
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

window.lb.createComponent(inputConfig, 'lbInputComp', 'input');
