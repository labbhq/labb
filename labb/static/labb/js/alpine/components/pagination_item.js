// pagination_item.js

const paginationItemConfig = {
  baseClasses: ["join-item", "btn"],
  variables: {
    active: {
        "default": false,
        "css_mapping": {
            "true": "btn-active"
        }
    },
    disabled: {
        "default": false,
        "css_mapping": {
            "true": "btn-disabled"
        }
    },
    size: {
        "default": "",
        "css_mapping": {
            "xs": "btn-xs",
            "sm": "btn-sm",
            "md": "btn-md",
            "lg": "btn-lg",
            "xl": "btn-xl"
        }
    },
  }
};

window.lb.createComponent(paginationItemConfig, 'lbPaginationItemComp', 'pagination.item');
