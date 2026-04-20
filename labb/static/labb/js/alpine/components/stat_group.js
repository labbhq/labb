// stat_group.js

const statGroupConfig = {
  baseClasses: ["stats"],
  variables: {
    direction: {
        "default": "horizontal",
        "css_mapping": {
            "horizontal": "stats-horizontal",
            "vertical": "stats-vertical"
        }
    },
  }
};

window.lb.createComponent(statGroupConfig, 'lbStatGroupComp', 'stat.group');
