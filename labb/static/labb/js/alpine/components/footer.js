// footer.js

const footerConfig = {
  baseClasses: ["footer"],
  variables: {
    center: {
        "default": false,
        "css_mapping": {
            "true": "footer-center"
        }
    },
    direction: {
        "default": "horizontal",
        "css_mapping": {
            "horizontal": "footer-horizontal",
            "vertical": "footer-vertical"
        }
    },
  }
};

window.lb.createComponent(footerConfig, 'lbFooterComp', 'footer');
