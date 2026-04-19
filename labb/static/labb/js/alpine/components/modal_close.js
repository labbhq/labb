// modal_close.js

const modalCloseConfig = {
  baseClasses: ["btn", "btn-sm", "btn-circle", "btn-ghost"],
  variables: {
    variant: {
        "default": "",
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
    position: {
        "default": "top-right",
        "css_mapping": {
            "top-right": "right-2 top-2",
            "top-left": "left-2 top-2",
            "bottom-right": "right-2 bottom-2",
            "bottom-left": "left-2 bottom-2"
        }
    },
  }
};

window.lb.createComponent(modalCloseConfig, 'lbModalCloseComp', 'modal.close');
