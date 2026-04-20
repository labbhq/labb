// tabs_content.js

const tabsContentConfig = {
  baseClasses: ["tab-content"],
  variables: {
    checked: {
        "default": false,
        "css_mapping": {
            "true": "tab-active"
        }
    },
    disabled: {
        "default": false,
        "css_mapping": {
            "true": "tab-disabled"
        }
    },
  }
};

window.lb.createComponent(tabsContentConfig, 'lbTabsContentComp', 'tabs.content');
