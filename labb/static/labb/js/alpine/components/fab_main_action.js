// fab_main_action.js

const fabMainActionConfig = {
  baseClasses: ["fab-main-action"],
  variables: {
    variant: {
        "default": "secondary",
        "css_mapping": {
            "neutral": "btn-neutral",
            "primary": "btn-primary",
            "secondary": "btn-secondary",
            "accent": "btn-accent",
            "info": "btn-info",
            "success": "btn-success",
            "warning": "btn-warning",
            "error": "btn-error"
        }
    },
    size: {
        "default": "lg",
        "css_mapping": {
            "xs": "btn-xs",
            "sm": "btn-sm",
            "md": "btn-md",
            "lg": "btn-lg",
            "xl": "btn-xl"
        }
    },
  }
};

window.lb.createComponent(fabMainActionConfig, 'lbFabMainActionComp', 'fab.main-action');
