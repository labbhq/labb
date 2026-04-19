// diff.js

const diffConfig = {
  baseClasses: ["diff"],
  variables: {
    aspectRatio: {
        "default": "",
        "css_mapping": {
            "16/9": "aspect-[16/9]",
            "4/3": "aspect-[4/3]",
            "1/1": "aspect-square",
            "3/4": "aspect-[3/4]",
            "9/16": "aspect-[9/16]"
        }
    },
  }
};

window.lb.createComponent(diffConfig, 'lbDiffComp', 'diff');
