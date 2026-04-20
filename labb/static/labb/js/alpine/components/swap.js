// swap.js

const swapConfig = {
  baseClasses: ["swap"],
  variables: {
    effect: {
        "default": "",
        "css_mapping": {
            "rotate": "swap-rotate",
            "flip": "swap-flip"
        }
    },
    checked: {
        "default": false,
        "css_mapping": {
            "true": "checked"
        }
    },
    disabled: {
        "default": false,
        "css_mapping": {
            "true": "disabled"
        }
    },
  }
};

window.lb.createComponent(swapConfig, 'lbSwapComp', 'swap');
