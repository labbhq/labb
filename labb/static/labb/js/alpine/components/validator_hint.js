// validator_hint.js

const validatorHintConfig = {
  baseClasses: ["validator-hint"],
  variables: {
    hidden: {
        "default": false,
        "css_mapping": {
            "true": "hidden"
        }
    },
  }
};

window.lb.createComponent(validatorHintConfig, 'lbValidatorHintComp', 'validator.hint');
