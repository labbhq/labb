// indicator_item.js

const indicatorItemConfig = {
  baseClasses: ["indicator-item"],
  variables: {
    horizontal: {
        "default": "",
        "css_mapping": {
            "start": "indicator-start",
            "center": "indicator-center",
            "end": "indicator-end"
        }
    },
    vertical: {
        "default": "",
        "css_mapping": {
            "top": "indicator-top",
            "middle": "indicator-middle",
            "bottom": "indicator-bottom"
        }
    },
  }
};

window.lb.createComponent(indicatorItemConfig, 'lbIndicatorItemComp', 'indicator.item');
