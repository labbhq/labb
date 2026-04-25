// radial_progress.js

const radialProgressConfig = {
  baseClasses: ["radial-progress"],
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
    bgVariant: {
        "default": "",
        "css_mapping": {
            "neutral": "bg-neutral text-neutral-content border-neutral",
            "primary": "bg-primary text-primary-content border-primary",
            "secondary": "bg-secondary text-secondary-content border-secondary",
            "accent": "bg-accent text-accent-content border-accent",
            "info": "bg-info text-info-content border-info",
            "success": "bg-success text-success-content border-success",
            "warning": "bg-warning text-warning-content border-warning",
            "error": "bg-error text-error-content border-error"
        }
    },
  }
};

window.lb.createComponent(radialProgressConfig, 'lbRadialProgressComp', 'radial-progress');
