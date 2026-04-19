// fab_close.js

const fabCloseConfig = {
  baseClasses: ["fab-close"],
  variables: {
    variant: {
        "default": "error",
        "css_mapping": {
            "neutral": "btn-neutral",
            "primary": "btn-primary",
            "secondary": "btn-secondary",
            "accent": "btn-accent",
            "info": "btn-info",
            "success": "btn-success",
            "warning": "btn-warning",
            "error": "btn-error"
        }
    },
    size: {
        "default": "lg",
        "css_mapping": {
            "xs": "btn-xs",
            "sm": "btn-sm",
            "md": "btn-md",
            "lg": "btn-lg",
            "xl": "btn-xl"
        }
    },
  }
};

window.lb.createComponent(fabCloseConfig, 'lbFabCloseComp', 'fab.close');
