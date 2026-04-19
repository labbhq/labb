// dock.js

const dockConfig = {
  baseClasses: ["dock"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "bg-neutral text-neutral-content",
            "primary": "bg-primary text-primary-content",
            "secondary": "bg-secondary text-secondary-content",
            "accent": "bg-accent text-accent-content",
            "info": "bg-info text-info-content",
            "success": "bg-success text-success-content",
            "warning": "bg-warning text-warning-content",
            "error": "bg-error text-error-content"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "dock-xs",
            "sm": "dock-sm",
            "md": "dock-md",
            "lg": "dock-lg",
            "xl": "dock-xl"
        }
    },
  }
};

window.lb.createComponent(dockConfig, 'lbDockComp', 'dock');
