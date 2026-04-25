// toast.js

const toastConfig = {
  baseClasses: ["toast"],
  variables: {
    horizontal: {
        "default": "",
        "css_mapping": {
            "start": "toast-start",
            "center": "toast-center",
            "end": "toast-end"
        }
    },
    vertical: {
        "default": "",
        "css_mapping": {
            "top": "toast-top",
            "middle": "toast-middle",
            "bottom": "toast-bottom"
        }
    },
  }
};

window.lb.createComponent(toastConfig, 'lbToastComp', 'toast');
