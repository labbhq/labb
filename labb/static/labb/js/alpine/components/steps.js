// steps.js

const stepsConfig = {
  baseClasses: ["steps"],
  variables: {
    direction: {
        "default": "horizontal",
        "css_mapping": {
            "horizontal": "steps-horizontal",
            "vertical": "steps-vertical"
        }
    },
  }
};

window.lb.createComponent(stepsConfig, 'lbStepsComp', 'steps');
