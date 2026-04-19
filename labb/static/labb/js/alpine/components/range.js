// range.js

const rangeConfig = {
  baseClasses: ["range"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "range-neutral",
            "primary": "range-primary",
            "secondary": "range-secondary",
            "accent": "range-accent",
            "info": "range-info",
            "success": "range-success",
            "warning": "range-warning",
            "error": "range-error"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "range-xs",
            "sm": "range-sm",
            "md": "range-md",
            "lg": "range-lg",
            "xl": "range-xl"
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

window.lb.createComponent(rangeConfig, 'lbRangeComp', 'range');
