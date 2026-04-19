// accordion_item.js

const accordionItemConfig = {
  baseClasses: ["collapse"],
  variables: {
    checked: {
        "default": false,
        "css_mapping": {
            "true": "checked"
        }
    },
    style: {
        "default": "",
        "css_mapping": {
            "arrow": "collapse-arrow",
            "plus": "collapse-plus"
        }
    },
    join: {
        "default": false,
        "css_mapping": {
            "true": "join-item"
        }
    },
    border: {
        "default": false,
        "css_mapping": {
            "true": "border border-base-300"
        }
    },
  }
};

window.lb.createComponent(accordionItemConfig, 'lbAccordionItemComp', 'accordion.item');
