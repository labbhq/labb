// radio.js

const radioConfig = {
  baseClasses: ["radio"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "radio-neutral",
            "primary": "radio-primary",
            "secondary": "radio-secondary",
            "accent": "radio-accent",
            "info": "radio-info",
            "success": "radio-success",
            "warning": "radio-warning",
            "error": "radio-error"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "radio-xs",
            "sm": "radio-sm",
            "md": "radio-md",
            "lg": "radio-lg",
            "xl": "radio-xl"
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

window.lb.createComponent(radioConfig, 'lbRadioComp', 'radio');
