// skeleton.js

const skeletonConfig = {
  baseClasses: ["skeleton"],
  variables: {
    text: {
        "default": false,
        "css_mapping": {
            "true": "skeleton-text"
        }
    },
  }
};

window.lb.createComponent(skeletonConfig, 'lbSkeletonComp', 'skeleton');
