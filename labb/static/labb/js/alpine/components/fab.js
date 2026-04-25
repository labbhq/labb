// fab.js

const fabConfig = {
  baseClasses: ["fab"],
  variables: {
    variant: {
        "default": "",
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
    flower: {
        "default": false,
        "css_mapping": {
            "true": "fab-flower"
        }
    },
  }
};

window.lb.createComponent(fabConfig, 'lbFabComp', 'fab');
