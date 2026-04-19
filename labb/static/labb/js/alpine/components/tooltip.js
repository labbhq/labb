// tooltip.js

const tooltipConfig = {
  baseClasses: ["tooltip"],
  variables: {
    placement: {
        "default": "top",
        "css_mapping": {
            "top": "tooltip-top",
            "bottom": "tooltip-bottom",
            "left": "tooltip-left",
            "right": "tooltip-right"
        }
    },
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "tooltip-neutral",
            "primary": "tooltip-primary",
            "secondary": "tooltip-secondary",
            "accent": "tooltip-accent",
            "info": "tooltip-info",
            "success": "tooltip-success",
            "warning": "tooltip-warning",
            "error": "tooltip-error"
        }
    },
    open: {
        "default": false,
        "css_mapping": {
            "true": "tooltip-open"
        }
    },
  }
};

window.lb.createComponent(tooltipConfig, 'lbTooltipComp', 'tooltip');
