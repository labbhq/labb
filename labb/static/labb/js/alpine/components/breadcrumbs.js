// breadcrumbs.js

const breadcrumbsConfig = {
  baseClasses: ["breadcrumbs"],
  variables: {
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "text-xs",
            "sm": "text-sm",
            "md": "text-base",
            "lg": "text-lg",
            "xl": "text-xl"
        }
    },
  }
};

window.lb.createComponent(breadcrumbsConfig, 'lbBreadcrumbsComp', 'breadcrumbs');
