// avatar.js

const avatarConfig = {
  baseClasses: ["avatar"],
  variables: {
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "w-8 text-xs",
            "sm": "w-12 text-md",
            "md": "w-16 text-lg",
            "lg": "w-24 text-xl",
            "xl": "w-32 text-2xl"
        }
    },
    rounded: {
        "default": "",
        "css_mapping": {
            "xs": "rounded-xs",
            "sm": "rounded-sm",
            "md": "rounded-md",
            "lg": "rounded-lg",
            "xl": "rounded-xl",
            "full": "rounded-full"
        }
    },
    mask: {
        "default": "",
        "css_mapping": {
            "heart": "mask mask-heart",
            "squircle": "mask mask-squircle",
            "hexagon-2": "mask mask-hexagon-2",
            "triangle": "mask mask-triangle",
            "pentagon": "mask mask-pentagon",
            "diamond": "mask mask-diamond",
            "star": "mask mask-star"
        }
    },
    status: {
        "default": "",
        "css_mapping": {
            "online": "avatar-online",
            "offline": "avatar-offline"
        }
    },
    placeholder: {
        "default": false,
        "css_mapping": {
            "true": "avatar-placeholder"
        }
    },
    ring: {
        "default": false,
        "css_mapping": {
            "true": "ring-2 ring-offset-2"
        }
    },
    ringColor: {
        "default": "",
        "css_mapping": {
            "primary": "ring-primary ring-offset-base-100",
            "secondary": "ring-secondary ring-offset-base-100",
            "accent": "ring-accent ring-offset-base-100",
            "neutral": "ring-neutral ring-offset-base-100",
            "info": "ring-info ring-offset-base-100",
            "success": "ring-success ring-offset-base-100",
            "warning": "ring-warning ring-offset-base-100",
            "error": "ring-error ring-offset-base-100"
        }
    },
    bgColor: {
        "default": "neutral",
        "css_mapping": {
            "neutral": "bg-neutral text-neutral-content",
            "primary": "bg-primary text-primary-content",
            "secondary": "bg-secondary text-secondary-content",
            "accent": "bg-accent text-accent-content",
            "info": "bg-info text-info-content",
            "success": "bg-success text-success-content",
            "warning": "bg-warning text-warning-content",
            "error": "bg-error text-error-content"
        }
    },
  }
};

window.lb.createComponent(avatarConfig, 'lbAvatarComp', 'avatar');
