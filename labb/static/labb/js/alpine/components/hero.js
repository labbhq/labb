// hero.js

const heroConfig = {
  baseClasses: ["hero"],
  variables: {
    overlay: {
        "default": false,
        "css_mapping": {
            "true": ""
        }
    },
  }
};

window.lb.createComponent(heroConfig, 'lbHeroComp', 'hero');
