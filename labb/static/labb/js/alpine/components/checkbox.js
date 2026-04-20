// checkbox.js

const checkboxConfig = {
  baseClasses: ["checkbox"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "primary": "checkbox-primary",
            "secondary": "checkbox-secondary",
            "accent": "checkbox-accent",
            "neutral": "checkbox-neutral",
            "info": "checkbox-info",
            "success": "checkbox-success",
            "warning": "checkbox-warning",
            "error": "checkbox-error"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "checkbox-xs",
            "sm": "checkbox-sm",
            "md": "checkbox-md",
            "lg": "checkbox-lg",
            "xl": "checkbox-xl"
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

window.lb.createComponent(checkboxConfig, 'lbCheckboxComp', 'checkbox');
