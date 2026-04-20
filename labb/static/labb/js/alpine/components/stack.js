// stack.js

const stackConfig = {
  baseClasses: ["stack"],
  variables: {
    direction: {
        "default": "",
        "css_mapping": {
            "top": "stack-top",
            "bottom": "stack-bottom",
            "start": "stack-start",
            "end": "stack-end"
        }
    },
  }
};

window.lb.createComponent(stackConfig, 'lbStackComp', 'stack');
