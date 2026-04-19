// stat_value.js

const statValueConfig = {
  baseClasses: ["stat-value"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "primary": "text-primary",
            "secondary": "text-secondary",
            "accent": "text-accent",
            "neutral": "text-neutral",
            "info": "text-info",
            "success": "text-success",
            "warning": "text-warning",
            "error": "text-error"
        }
    },
  }
};

window.lb.createComponent(statValueConfig, 'lbStatValueComp', 'stat.value');
