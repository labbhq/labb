// text.js

const textConfig = {
  baseClasses: [],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "text-neutral",
            "primary": "text-primary",
            "secondary": "text-secondary",
            "accent": "text-accent",
            "info": "text-info",
            "success": "text-success",
            "warning": "text-warning",
            "error": "text-error"
        }
    },
    size: {
        "default": "",
        "css_mapping": {
            "xs": "text-xs",
            "sm": "text-sm",
            "md": "text-base",
            "lg": "text-lg",
            "xl": "text-xl",
            "2xl": "text-2xl",
            "3xl": "text-3xl",
            "4xl": "text-4xl"
        }
    },
    underline: {
        "default": false,
        "css_mapping": {
            "true": "underline"
        }
    },
  }
};

window.lb.createComponent(textConfig, 'lbTextComp', 'text');
