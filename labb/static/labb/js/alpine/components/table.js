// table.js

const tableConfig = {
  baseClasses: ["table"],
  variables: {
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "table-xs",
            "sm": "table-sm",
            "md": "table-md",
            "lg": "table-lg",
            "xl": "table-xl"
        }
    },
    zebra: {
        "default": false,
        "css_mapping": {
            "true": "table-zebra"
        }
    },
    pinRows: {
        "default": false,
        "css_mapping": {
            "true": "table-pin-rows"
        }
    },
    pinCols: {
        "default": false,
        "css_mapping": {
            "true": "table-pin-cols"
        }
    },
  }
};

window.lb.createComponent(tableConfig, 'lbTableComp', 'table');
