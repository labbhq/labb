// progress.js

const progressConfig = {
  baseClasses: ["progress"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "progress-neutral",
            "primary": "progress-primary",
            "secondary": "progress-secondary",
            "accent": "progress-accent",
            "info": "progress-info",
            "success": "progress-success",
            "warning": "progress-warning",
            "error": "progress-error"
        }
    },
  }
};

window.lb.createComponent(progressConfig, 'lbProgressComp', 'progress');
