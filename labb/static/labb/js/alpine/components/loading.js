// loading.js

const loadingConfig = {
  baseClasses: ["loading"],
  variables: {
    type: {
        "default": "spinner",
        "css_mapping": {
            "spinner": "loading-spinner",
            "dots": "loading-dots",
            "ring": "loading-ring",
            "ball": "loading-ball",
            "bars": "loading-bars",
            "infinity": "loading-infinity"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "loading-xs",
            "sm": "loading-sm",
            "md": "loading-md",
            "lg": "loading-lg",
            "xl": "loading-xl"
        }
    },
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
  }
};

window.lb.createComponent(loadingConfig, 'lbLoadingComp', 'loading');
