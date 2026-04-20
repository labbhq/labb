// steps_item.js

const stepsItemConfig = {
  baseClasses: ["step"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "step-neutral",
            "primary": "step-primary",
            "secondary": "step-secondary",
            "accent": "step-accent",
            "info": "step-info",
            "success": "step-success",
            "warning": "step-warning",
            "error": "step-error"
        }
    },
  }
};

window.lb.createComponent(stepsItemConfig, 'lbStepsItemComp', 'steps.item');
