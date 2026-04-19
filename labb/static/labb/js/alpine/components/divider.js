// divider.js

const dividerConfig = {
  baseClasses: ["divider"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "divider-neutral",
            "primary": "divider-primary",
            "secondary": "divider-secondary",
            "accent": "divider-accent",
            "info": "divider-info",
            "success": "divider-success",
            "warning": "divider-warning",
            "error": "divider-error"
        }
    },
    direction: {
        "default": "",
        "css_mapping": {
            "horizontal": "divider-horizontal",
            "vertical": "divider-vertical"
        }
    },
    position: {
        "default": "",
        "css_mapping": {
            "start": "divider-start",
            "end": "divider-end"
        }
    },
  }
};

window.lb.createComponent(dividerConfig, 'lbDividerComp', 'divider');
