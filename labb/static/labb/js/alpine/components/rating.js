// rating.js

const ratingConfig = {
  baseClasses: ["rating"],
  variables: {
    shape: {
        "default": "star-2",
        "css_mapping": {
            "star": "mask-star",
            "star-2": "mask-star-2",
            "heart": "mask-heart",
            "diamond": "mask-diamond",
            "circle": "mask-circle",
            "squircle": "mask-squircle",
            "hexagon": "mask-hexagon",
            "hexagon-2": "mask-hexagon-2",
            "decagon": "mask-decagon",
            "pentagon": "mask-pentagon",
            "triangle": "mask-triangle"
        }
    },
    variant: {
        "default": "",
        "css_mapping": {
            "neutral": "bg-neutral",
            "primary": "bg-primary",
            "secondary": "bg-secondary",
            "accent": "bg-accent",
            "info": "bg-info",
            "success": "bg-success",
            "warning": "bg-warning",
            "error": "bg-error"
        }
    },
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "rating-xs",
            "sm": "rating-sm",
            "md": "rating-md",
            "lg": "rating-lg",
            "xl": "rating-xl"
        }
    },
    half: {
        "default": false,
        "css_mapping": {
            "true": "rating-half"
        }
    },
  }
};

window.lb.createComponent(ratingConfig, 'lbRatingComp', 'rating');
