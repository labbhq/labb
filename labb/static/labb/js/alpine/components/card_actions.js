// card_actions.js

const cardActionsConfig = {
  baseClasses: ["card-actions"],
  variables: {
    justify: {
        "default": "",
        "css_mapping": {
            "start": "justify-start",
            "center": "justify-center",
            "end": "justify-end",
            "between": "justify-between",
            "around": "justify-around",
            "evenly": "justify-evenly"
        }
    },
  }
};

window.lb.createComponent(cardActionsConfig, 'lbCardActionsComp', 'card.actions');
