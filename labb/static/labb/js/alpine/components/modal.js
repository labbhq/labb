// modal.js

const modalConfig = {
  baseClasses: ["modal"],
  variables: {
    placement: {
        "default": "middle",
        "css_mapping": {
            "top": "modal-top",
            "middle": "modal-middle",
            "bottom": "modal-bottom",
            "start": "modal-start",
            "end": "modal-end"
        }
    },
    open: {
        "default": false,
        "css_mapping": {
            "true": "modal-open"
        }
    },
  }
};

window.lb.createComponent(modalConfig, 'lbModalComp', 'modal');
