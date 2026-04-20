// button.js

const buttonConfig = {
  baseClasses: ["btn"],
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
    btnStyle: {
        "default": "",
        "css_mapping": {
            "outline": "btn-outline",
            "dash": "btn-dash",
            "soft": "btn-soft",
            "ghost": "btn-ghost",
            "link": "btn-link"
        }
    },
    behavior: {
        "default": "",
        "css_mapping": {
            "active": "btn-active",
            "disabled": "btn-disabled"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "btn-xs",
            "sm": "btn-sm",
            "md": "btn-md",
            "lg": "btn-lg",
            "xl": "btn-xl"
        }
    },
    modifier: {
        "default": "",
        "css_mapping": {
            "wide": "btn-wide",
            "block": "btn-block",
            "square": "btn-square",
            "circle": "btn-circle"
        }
    },
  }
};

window.lb.createComponent(buttonConfig, 'lbButtonComp', 'button');
