// file_input.js

const fileInputConfig = {
  baseClasses: ["file-input"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "file-input-neutral",
            "primary": "file-input-primary",
            "secondary": "file-input-secondary",
            "accent": "file-input-accent",
            "info": "file-input-info",
            "success": "file-input-success",
            "warning": "file-input-warning",
            "error": "file-input-error"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "file-input-xs",
            "sm": "file-input-sm",
            "md": "file-input-md",
            "lg": "file-input-lg",
            "xl": "file-input-xl"
        }
    },
    ghost: {
        "default": false,
        "css_mapping": {
            "true": "file-input-ghost"
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

window.lb.createComponent(fileInputConfig, 'lbFileInputComp', 'file-input');
