// textarea.js

const textareaConfig = {
  baseClasses: ["textarea"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "textarea-neutral",
            "primary": "textarea-primary",
            "secondary": "textarea-secondary",
            "accent": "textarea-accent",
            "info": "textarea-info",
            "success": "textarea-success",
            "warning": "textarea-warning",
            "error": "textarea-error"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "textarea-xs",
            "sm": "textarea-sm",
            "md": "textarea-md",
            "lg": "textarea-lg",
            "xl": "textarea-xl"
        }
    },
    ghost: {
        "default": false,
        "css_mapping": {
            "true": "textarea-ghost"
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

window.lb.createComponent(textareaConfig, 'lbTextareaComp', 'textarea');
