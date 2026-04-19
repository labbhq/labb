// dropdown.js

const dropdownConfig = {
  baseClasses: ["dropdown"],
  variables: {
    placement: {
        "default": "bottom",
        "css_mapping": {
            "top": "dropdown-top",
            "left": "dropdown-left",
            "right": "dropdown-right"
        }
    },
    alignment: {
        "default": "",
        "css_mapping": {
            "start": "dropdown-start",
            "center": "dropdown-center",
            "end": "dropdown-end"
        }
    },
    hover: {
        "default": false,
        "css_mapping": {
            "true": "dropdown-hover"
        }
    },
    open: {
        "default": false,
        "css_mapping": {
            "true": "dropdown-open"
        }
    },
  }
};

window.lb.createComponent(dropdownConfig, 'lbDropdownComp', 'dropdown');
