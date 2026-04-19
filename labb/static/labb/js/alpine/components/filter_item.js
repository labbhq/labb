// filter_item.js

const filterItemConfig = {
  baseClasses: ["btn"],
  variables: {
    reset: {
        "default": false,
        "css_mapping": {
            "true": "filter-reset"
        }
    },
  }
};

window.lb.createComponent(filterItemConfig, 'lbFilterItemComp', 'filter.item');
