// mask.js

const maskConfig = {
  baseClasses: ["mask"],
  variables: {
    shape: {
        "default": "squircle",
        "css_mapping": {
            "squircle": "mask-squircle",
            "heart": "mask-heart",
            "hexagon": "mask-hexagon",
            "hexagon-2": "mask-hexagon-2",
            "decagon": "mask-decagon",
            "pentagon": "mask-pentagon",
            "diamond": "mask-diamond",
            "square": "mask-square",
            "circle": "mask-circle",
            "star": "mask-star",
            "star-2": "mask-star-2",
            "triangle": "mask-triangle",
            "triangle-2": "mask-triangle-2",
            "triangle-3": "mask-triangle-3",
            "triangle-4": "mask-triangle-4"
        }
    },
    half: {
        "default": "",
        "css_mapping": {
            "1": "mask-half-1",
            "2": "mask-half-2"
        }
    },
  }
};

window.lb.createComponent(maskConfig, 'lbMaskComp', 'mask');
