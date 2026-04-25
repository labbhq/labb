// card.js

const cardConfig = {
  baseClasses: ["card"],
  variables: {
    variant: {
        "default": "default",
        "css_mapping": {
            "primary": "bg-primary text-primary-content",
            "secondary": "bg-secondary text-secondary-content",
            "accent": "bg-accent text-accent-content",
            "neutral": "bg-neutral text-neutral-content",
            "info": "bg-info text-info-content",
            "success": "bg-success text-success-content",
            "warning": "bg-warning text-warning-content",
            "error": "bg-error text-error-content"
        }
    },
    border: {
        "default": false,
        "css_mapping": {
            "true": "card-border"
        }
    },
    dash: {
        "default": false,
        "css_mapping": {
            "true": "card-dash"
        }
    },
    side: {
        "default": false,
        "css_mapping": {
            "true": "card-side"
        }
    },
    imageFull: {
        "default": false,
        "css_mapping": {
            "true": "image-full"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "card-xs",
            "sm": "card-sm",
            "md": "card-md",
            "lg": "card-lg",
            "xl": "card-xl"
        }
    },
  }
};

window.lb.createComponent(cardConfig, 'lbCardComp', 'card');
