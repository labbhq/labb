// join.js

const joinConfig = {
  baseClasses: ["join"],
  variables: {
    direction: {
        "default": "",
        "css_mapping": {
            "horizontal": "join-horizontal",
            "vertical": "join-vertical"
        }
    },
  }
};

window.lb.createComponent(joinConfig, 'lbJoinComp', 'join');
