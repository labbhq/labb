// link.js

const linkConfig = {
  baseClasses: ["link"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "link-neutral",
            "primary": "link-primary",
            "secondary": "link-secondary",
            "accent": "link-accent",
            "info": "link-info",
            "success": "link-success",
            "warning": "link-warning",
            "error": "link-error"
        }
    },
    hover: {
        "default": false,
        "css_mapping": {
            "true": "link-hover"
        }
    },
  }
};

window.lb.createComponent(linkConfig, 'lbLinkComp', 'link');
