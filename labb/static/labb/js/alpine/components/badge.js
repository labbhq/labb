// badge.js

const badgeConfig = {
  baseClasses: ["badge"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "badge-neutral",
            "primary": "badge-primary",
            "secondary": "badge-secondary",
            "accent": "badge-accent",
            "info": "badge-info",
            "success": "badge-success",
            "warning": "badge-warning",
            "error": "badge-error"
        }
    },
    style: {
        "default": "",
        "css_mapping": {
            "outline": "badge-outline",
            "dash": "badge-dash",
            "soft": "badge-soft",
            "ghost": "badge-ghost"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "badge-xs",
            "sm": "badge-sm",
            "md": "badge-md",
            "lg": "badge-lg",
            "xl": "badge-xl"
        }
    },
  }
};

window.lb.createComponent(badgeConfig, 'lbBadgeComp', 'badge');
