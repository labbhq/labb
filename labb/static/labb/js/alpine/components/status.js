// status.js

const statusConfig = {
  baseClasses: ["status"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "status-neutral",
            "primary": "status-primary",
            "secondary": "status-secondary",
            "accent": "status-accent",
            "info": "status-info",
            "success": "status-success",
            "warning": "status-warning",
            "error": "status-error"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "status-xs",
            "sm": "status-sm",
            "md": "status-md",
            "lg": "status-lg",
            "xl": "status-xl"
        }
    },
    animate: {
        "default": "",
        "css_mapping": {
            "ping": "animate-ping",
            "bounce": "animate-bounce"
        }
    },
  }
};

window.lb.createComponent(statusConfig, 'lbStatusComp', 'status');
