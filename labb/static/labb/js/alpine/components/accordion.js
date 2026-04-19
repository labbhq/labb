// accordion.js

const accordionConfig = {
  baseClasses: [],
  variables: {
    join: {
        "default": false,
        "css_mapping": {
            "true": "join join-vertical"
        }
    },
  }
};

window.lb.createComponent(accordionConfig, 'lbAccordionComp', 'accordion');
