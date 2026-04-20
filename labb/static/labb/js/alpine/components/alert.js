// alert.js

const alertConfig = {
  baseClasses: ["alert"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "info": "alert-info",
            "success": "alert-success",
            "warning": "alert-warning",
            "error": "alert-error"
        }
    },
    alertStyle: {
        "default": "",
        "css_mapping": {
            "outline": "alert-outline",
            "dash": "alert-dash",
            "soft": "alert-soft"
        }
    },
    direction: {
        "default": "",
        "css_mapping": {
            "vertical": "alert-vertical",
            "horizontal": "alert-horizontal"
        }
    },
  }
};

window.lb.createComponent(alertConfig, 'lbAlertComp', 'alert');
