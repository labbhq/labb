window.lb = window.lb || {};
window.lb._schemas = {
  "accordion": {
    "base": [],
    "join": {
      "true": "join join-vertical"
    }
  },
  "accordion.item": {
    "base": [
      "collapse"
    ],
    "style": {
      "arrow": "collapse-arrow",
      "plus": "collapse-plus"
    },
    "join": {
      "true": "join-item"
    },
    "border": {
      "true": "border border-base-300"
    }
  },
  "alert": {
    "base": [
      "alert"
    ],
    "variant": {
      "info": "alert-info",
      "success": "alert-success",
      "warning": "alert-warning",
      "error": "alert-error"
    },
    "alertStyle": {
      "outline": "alert-outline",
      "dash": "alert-dash",
      "soft": "alert-soft"
    },
    "direction": {
      "vertical": "alert-vertical",
      "horizontal": "alert-horizontal"
    }
  },
  "aura": {
    "base": [
      "aura"
    ],
    "variant": {
      "dual": "aura-dual",
      "rainbow": "aura-rainbow",
      "holo": "aura-holo",
      "gold": "aura-gold",
      "silver": "aura-silver",
      "glow": "aura-glow"
    },
    "size": {
      "xs": "aura-xs",
      "sm": "aura-sm",
      "md": "aura-md",
      "lg": "aura-lg",
      "xl": "aura-xl"
    }
  },
  "avatar": {
    "base": [
      "avatar"
    ],
    "size": {
      "xs": "w-8 text-xs",
      "sm": "w-12 text-md",
      "md": "w-16 text-lg",
      "lg": "w-24 text-xl",
      "xl": "w-32 text-2xl"
    },
    "rounded": {
      "xs": "rounded-xs",
      "sm": "rounded-sm",
      "md": "rounded-md",
      "lg": "rounded-lg",
      "xl": "rounded-xl",
      "full": "rounded-full"
    },
    "mask": {
      "heart": "mask mask-heart",
      "squircle": "mask mask-squircle",
      "hexagon-2": "mask mask-hexagon-2",
      "triangle": "mask mask-triangle",
      "pentagon": "mask mask-pentagon",
      "diamond": "mask mask-diamond",
      "star": "mask mask-star"
    },
    "status": {
      "online": "avatar-online",
      "offline": "avatar-offline"
    },
    "placeholder": {
      "true": "avatar-placeholder"
    },
    "ring": {
      "true": "ring-2 ring-offset-2"
    },
    "ringColor": {
      "primary": "ring-primary ring-offset-base-100",
      "secondary": "ring-secondary ring-offset-base-100",
      "accent": "ring-accent ring-offset-base-100",
      "neutral": "ring-neutral ring-offset-base-100",
      "info": "ring-info ring-offset-base-100",
      "success": "ring-success ring-offset-base-100",
      "warning": "ring-warning ring-offset-base-100",
      "error": "ring-error ring-offset-base-100"
    },
    "bgColor": {
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
  "avatar.group": {
    "base": [
      "avatar-group"
    ],
    "spacing": {
      "wide": "",
      "normal": "-space-x-2",
      "tight": "-space-x-6",
      "tighter": "-space-x-8",
      "tightest": "-space-x-12"
    }
  },
  "badge": {
    "base": [
      "badge"
    ],
    "variant": {
      "neutral": "badge-neutral",
      "primary": "badge-primary",
      "secondary": "badge-secondary",
      "accent": "badge-accent",
      "info": "badge-info",
      "success": "badge-success",
      "warning": "badge-warning",
      "error": "badge-error"
    },
    "style": {
      "outline": "badge-outline",
      "dash": "badge-dash",
      "soft": "badge-soft",
      "ghost": "badge-ghost"
    },
    "size": {
      "xs": "badge-xs",
      "sm": "badge-sm",
      "md": "badge-md",
      "lg": "badge-lg",
      "xl": "badge-xl"
    }
  },
  "breadcrumbs": {
    "base": [
      "breadcrumbs"
    ],
    "size": {
      "xs": "text-xs",
      "sm": "text-sm",
      "md": "text-base",
      "lg": "text-lg",
      "xl": "text-xl"
    }
  },
  "button": {
    "base": [
      "btn"
    ],
    "variant": {
      "neutral": "btn-neutral",
      "primary": "btn-primary",
      "secondary": "btn-secondary",
      "accent": "btn-accent",
      "info": "btn-info",
      "success": "btn-success",
      "warning": "btn-warning",
      "error": "btn-error"
    },
    "btnStyle": {
      "outline": "btn-outline",
      "dash": "btn-dash",
      "soft": "btn-soft",
      "ghost": "btn-ghost",
      "link": "btn-link"
    },
    "behavior": {
      "active": "btn-active",
      "disabled": "btn-disabled"
    },
    "size": {
      "xs": "btn-xs",
      "sm": "btn-sm",
      "md": "btn-md",
      "lg": "btn-lg",
      "xl": "btn-xl"
    },
    "modifier": {
      "wide": "btn-wide",
      "block": "btn-block",
      "square": "btn-square",
      "circle": "btn-circle"
    }
  },
  "card": {
    "base": [
      "card"
    ],
    "variant": {
      "primary": "bg-primary text-primary-content",
      "secondary": "bg-secondary text-secondary-content",
      "accent": "bg-accent text-accent-content",
      "neutral": "bg-neutral text-neutral-content",
      "info": "bg-info text-info-content",
      "success": "bg-success text-success-content",
      "warning": "bg-warning text-warning-content",
      "error": "bg-error text-error-content"
    },
    "border": {
      "true": "card-border"
    },
    "dash": {
      "true": "card-dash"
    },
    "side": {
      "true": "card-side"
    },
    "imageFull": {
      "true": "image-full"
    },
    "size": {
      "xs": "card-xs",
      "sm": "card-sm",
      "md": "card-md",
      "lg": "card-lg",
      "xl": "card-xl"
    }
  },
  "card.actions": {
    "base": [
      "card-actions"
    ],
    "justify": {
      "start": "justify-start",
      "center": "justify-center",
      "end": "justify-end",
      "between": "justify-between",
      "around": "justify-around",
      "evenly": "justify-evenly"
    }
  },
  "carousel": {
    "base": [
      "carousel"
    ],
    "snap": {
      "start": "carousel-start",
      "center": "carousel-center",
      "end": "carousel-end"
    },
    "direction": {
      "horizontal": "",
      "vertical": "carousel-vertical"
    }
  },
  "chat": {
    "base": [
      "chat"
    ],
    "placement": {
      "start": "chat-start",
      "end": "chat-end"
    }
  },
  "chat.bubble": {
    "base": [
      "chat-bubble"
    ],
    "variant": {
      "primary": "chat-bubble-primary",
      "secondary": "chat-bubble-secondary",
      "accent": "chat-bubble-accent",
      "neutral": "chat-bubble-neutral",
      "info": "chat-bubble-info",
      "success": "chat-bubble-success",
      "warning": "chat-bubble-warning",
      "error": "chat-bubble-error"
    }
  },
  "chat.image": {
    "base": [
      "chat-image",
      "avatar"
    ],
    "size": {
      "sm": "w-8",
      "md": "w-10",
      "lg": "w-12"
    }
  },
  "checkbox": {
    "base": [
      "checkbox"
    ],
    "variant": {
      "primary": "checkbox-primary",
      "secondary": "checkbox-secondary",
      "accent": "checkbox-accent",
      "neutral": "checkbox-neutral",
      "info": "checkbox-info",
      "success": "checkbox-success",
      "warning": "checkbox-warning",
      "error": "checkbox-error"
    },
    "size": {
      "xs": "checkbox-xs",
      "sm": "checkbox-sm",
      "md": "checkbox-md",
      "lg": "checkbox-lg",
      "xl": "checkbox-xl"
    },
    "validate": {
      "true": "validator"
    }
  },
  "collapse": {
    "base": [
      "collapse"
    ],
    "style": {
      "arrow": "collapse-arrow",
      "plus": "collapse-plus"
    },
    "open": {
      "true": "collapse-open"
    }
  },
  "diff": {
    "base": [
      "diff"
    ],
    "aspectRatio": {
      "16/9": "aspect-[16/9]",
      "4/3": "aspect-[4/3]",
      "1/1": "aspect-square",
      "3/4": "aspect-[3/4]",
      "9/16": "aspect-[9/16]"
    }
  },
  "divider": {
    "base": [
      "divider"
    ],
    "variant": {
      "neutral": "divider-neutral",
      "primary": "divider-primary",
      "secondary": "divider-secondary",
      "accent": "divider-accent",
      "info": "divider-info",
      "success": "divider-success",
      "warning": "divider-warning",
      "error": "divider-error"
    },
    "direction": {
      "horizontal": "divider-horizontal",
      "vertical": "divider-vertical"
    },
    "position": {
      "start": "divider-start",
      "end": "divider-end"
    }
  },
  "dock": {
    "base": [
      "dock"
    ],
    "variant": {
      "neutral": "bg-neutral text-neutral-content",
      "primary": "bg-primary text-primary-content",
      "secondary": "bg-secondary text-secondary-content",
      "accent": "bg-accent text-accent-content",
      "info": "bg-info text-info-content",
      "success": "bg-success text-success-content",
      "warning": "bg-warning text-warning-content",
      "error": "bg-error text-error-content"
    },
    "size": {
      "xs": "dock-xs",
      "sm": "dock-sm",
      "md": "dock-md",
      "lg": "dock-lg",
      "xl": "dock-xl"
    }
  },
  "drawer": {
    "base": [
      "drawer"
    ],
    "end": {
      "true": "drawer-end"
    },
    "open": {
      "true": "drawer-open"
    }
  },
  "dropdown": {
    "base": [
      "dropdown"
    ],
    "placement": {
      "top": "dropdown-top",
      "left": "dropdown-left",
      "right": "dropdown-right"
    },
    "alignment": {
      "start": "dropdown-start",
      "center": "dropdown-center",
      "end": "dropdown-end"
    },
    "hover": {
      "true": "dropdown-hover"
    },
    "open": {
      "true": "dropdown-open"
    }
  },
  "fab": {
    "base": [
      "fab"
    ],
    "variant": {
      "neutral": "btn-neutral",
      "primary": "btn-primary",
      "secondary": "btn-secondary",
      "accent": "btn-accent",
      "info": "btn-info",
      "success": "btn-success",
      "warning": "btn-warning",
      "error": "btn-error"
    },
    "size": {
      "xs": "btn-xs",
      "sm": "btn-sm",
      "md": "btn-md",
      "lg": "btn-lg",
      "xl": "btn-xl"
    },
    "flower": {
      "true": "fab-flower"
    }
  },
  "fab.close": {
    "base": [
      "fab-close"
    ],
    "variant": {
      "neutral": "btn-neutral",
      "primary": "btn-primary",
      "secondary": "btn-secondary",
      "accent": "btn-accent",
      "info": "btn-info",
      "success": "btn-success",
      "warning": "btn-warning",
      "error": "btn-error"
    },
    "size": {
      "xs": "btn-xs",
      "sm": "btn-sm",
      "md": "btn-md",
      "lg": "btn-lg",
      "xl": "btn-xl"
    }
  },
  "fab.main-action": {
    "base": [
      "fab-main-action"
    ],
    "variant": {
      "neutral": "btn-neutral",
      "primary": "btn-primary",
      "secondary": "btn-secondary",
      "accent": "btn-accent",
      "info": "btn-info",
      "success": "btn-success",
      "warning": "btn-warning",
      "error": "btn-error"
    },
    "size": {
      "xs": "btn-xs",
      "sm": "btn-sm",
      "md": "btn-md",
      "lg": "btn-lg",
      "xl": "btn-xl"
    }
  },
  "file-input": {
    "base": [
      "file-input"
    ],
    "variant": {
      "neutral": "file-input-neutral",
      "primary": "file-input-primary",
      "secondary": "file-input-secondary",
      "accent": "file-input-accent",
      "info": "file-input-info",
      "success": "file-input-success",
      "warning": "file-input-warning",
      "error": "file-input-error"
    },
    "size": {
      "xs": "file-input-xs",
      "sm": "file-input-sm",
      "md": "file-input-md",
      "lg": "file-input-lg",
      "xl": "file-input-xl"
    },
    "ghost": {
      "true": "file-input-ghost"
    },
    "validate": {
      "true": "validator"
    }
  },
  "filter.item": {
    "base": [
      "btn"
    ],
    "reset": {
      "true": "filter-reset"
    }
  },
  "footer": {
    "base": [
      "footer"
    ],
    "center": {
      "true": "footer-center"
    },
    "direction": {
      "horizontal": "footer-horizontal",
      "vertical": "footer-vertical"
    }
  },
  "hero": {
    "base": [
      "hero"
    ],
    "overlay": {
      "true": ""
    }
  },
  "indicator.item": {
    "base": [
      "indicator-item"
    ],
    "horizontal": {
      "start": "indicator-start",
      "center": "indicator-center",
      "end": "indicator-end"
    },
    "vertical": {
      "top": "indicator-top",
      "middle": "indicator-middle",
      "bottom": "indicator-bottom"
    }
  },
  "input": {
    "base": [
      "input"
    ],
    "variant": {
      "neutral": "input-neutral",
      "primary": "input-primary",
      "secondary": "input-secondary",
      "accent": "input-accent",
      "info": "input-info",
      "success": "input-success",
      "warning": "input-warning",
      "error": "input-error"
    },
    "size": {
      "xs": "input-xs",
      "sm": "input-sm",
      "md": "input-md",
      "lg": "input-lg",
      "xl": "input-xl"
    },
    "ghost": {
      "true": "input-ghost"
    },
    "validate": {
      "true": "validator"
    }
  },
  "join": {
    "base": [
      "join"
    ],
    "direction": {
      "horizontal": "join-horizontal",
      "vertical": "join-vertical"
    }
  },
  "kbd": {
    "base": [
      "kbd"
    ],
    "size": {
      "xs": "kbd-xs",
      "sm": "kbd-sm",
      "md": "kbd-md",
      "lg": "kbd-lg",
      "xl": "kbd-xl"
    },
    "variant": {
      "neutral": "bg-neutral/15 text-neutral border-neutral/25",
      "primary": "bg-primary/15 text-primary border-primary/25",
      "secondary": "bg-secondary/15 text-secondary border-secondary/25",
      "accent": "bg-accent/15 text-accent border-accent/25",
      "info": "bg-info/15 text-info border-info/25",
      "success": "bg-success/15 text-success border-success/25",
      "warning": "bg-warning/15 text-warning border-warning/25",
      "error": "bg-error/15 text-error border-error/25"
    }
  },
  "link": {
    "base": [
      "link"
    ],
    "variant": {
      "neutral": "link-neutral",
      "primary": "link-primary",
      "secondary": "link-secondary",
      "accent": "link-accent",
      "info": "link-info",
      "success": "link-success",
      "warning": "link-warning",
      "error": "link-error"
    },
    "hover": {
      "true": "link-hover"
    }
  },
  "loading": {
    "base": [
      "loading"
    ],
    "type": {
      "spinner": "loading-spinner",
      "dots": "loading-dots",
      "ring": "loading-ring",
      "ball": "loading-ball",
      "bars": "loading-bars",
      "infinity": "loading-infinity"
    },
    "size": {
      "xs": "loading-xs",
      "sm": "loading-sm",
      "md": "loading-md",
      "lg": "loading-lg",
      "xl": "loading-xl"
    },
    "variant": {
      "neutral": "text-neutral",
      "primary": "text-primary",
      "secondary": "text-secondary",
      "accent": "text-accent",
      "info": "text-info",
      "success": "text-success",
      "warning": "text-warning",
      "error": "text-error"
    }
  },
  "mask": {
    "base": [
      "mask"
    ],
    "shape": {
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
    },
    "half": {
      "1": "mask-half-1",
      "2": "mask-half-2"
    }
  },
  "menu": {
    "base": [
      "menu"
    ],
    "direction": {
      "vertical": "menu-vertical",
      "horizontal": "menu-horizontal"
    },
    "size": {
      "xs": "menu-xs",
      "sm": "menu-sm",
      "md": "menu-md",
      "lg": "menu-lg",
      "xl": "menu-xl"
    }
  },
  "menu.item": {
    "base": [],
    "type": {
      "title": "menu-title",
      "submenu-details": "menu-dropdown",
      "submenu-toggle": "menu-dropdown-toggle"
    },
    "size": {
      "xs": "menu-xs",
      "sm": "menu-sm",
      "md": "menu-md",
      "lg": "menu-lg",
      "xl": "menu-xl"
    },
    "disabled": {
      "true": "menu-disabled"
    },
    "active": {
      "true": "menu-active"
    },
    "open": {
      "true": "menu-dropdown-show"
    }
  },
  "modal": {
    "base": [
      "modal"
    ],
    "placement": {
      "top": "modal-top",
      "middle": "modal-middle",
      "bottom": "modal-bottom",
      "start": "modal-start",
      "end": "modal-end"
    },
    "open": {
      "true": "modal-open"
    }
  },
  "modal.box": {
    "base": [
      "modal-box"
    ],
    "size": {
      "xs": "w-11/12 sm:w-72 max-w-xs",
      "sm": "w-11/12 sm:w-80 max-w-sm",
      "md": "w-11/12 sm:w-96 max-w-md",
      "lg": "w-11/12 sm:w-[32rem] max-w-lg",
      "xl": "w-11/12 sm:w-[36rem] max-w-xl",
      "screen": "w-11/12 max-w-5xl"
    }
  },
  "modal.close": {
    "base": [
      "btn",
      "btn-sm",
      "btn-circle",
      "btn-ghost"
    ],
    "variant": {
      "neutral": "btn-neutral",
      "primary": "btn-primary",
      "secondary": "btn-secondary",
      "accent": "btn-accent",
      "info": "btn-info",
      "success": "btn-success",
      "warning": "btn-warning",
      "error": "btn-error"
    },
    "position": {
      "top-right": "right-2 top-2",
      "top-left": "left-2 top-2",
      "bottom-right": "right-2 bottom-2",
      "bottom-left": "left-2 bottom-2"
    }
  },
  "otp": {
    "base": [
      "otp"
    ],
    "size": {
      "xs": "otp-xs",
      "sm": "otp-sm",
      "md": "otp-md",
      "lg": "otp-lg",
      "xl": "otp-xl"
    },
    "variant": {
      "neutral": "otp-neutral",
      "primary": "otp-primary",
      "secondary": "otp-secondary",
      "accent": "otp-accent",
      "info": "otp-info",
      "success": "otp-success",
      "warning": "otp-warning",
      "error": "otp-error"
    },
    "joined": {
      "true": "otp-joined"
    }
  },
  "pagination.item": {
    "base": [
      "join-item",
      "btn"
    ],
    "active": {
      "true": "btn-active"
    },
    "disabled": {
      "true": "btn-disabled"
    },
    "size": {
      "xs": "btn-xs",
      "sm": "btn-sm",
      "md": "btn-md",
      "lg": "btn-lg",
      "xl": "btn-xl"
    }
  },
  "progress": {
    "base": [
      "progress"
    ],
    "variant": {
      "neutral": "progress-neutral",
      "primary": "progress-primary",
      "secondary": "progress-secondary",
      "accent": "progress-accent",
      "info": "progress-info",
      "success": "progress-success",
      "warning": "progress-warning",
      "error": "progress-error"
    }
  },
  "radial-progress": {
    "base": [
      "radial-progress"
    ],
    "variant": {
      "neutral": "text-neutral",
      "primary": "text-primary",
      "secondary": "text-secondary",
      "accent": "text-accent",
      "info": "text-info",
      "success": "text-success",
      "warning": "text-warning",
      "error": "text-error"
    },
    "bgVariant": {
      "neutral": "bg-neutral text-neutral-content border-neutral",
      "primary": "bg-primary text-primary-content border-primary",
      "secondary": "bg-secondary text-secondary-content border-secondary",
      "accent": "bg-accent text-accent-content border-accent",
      "info": "bg-info text-info-content border-info",
      "success": "bg-success text-success-content border-success",
      "warning": "bg-warning text-warning-content border-warning",
      "error": "bg-error text-error-content border-error"
    }
  },
  "radio": {
    "base": [
      "radio"
    ],
    "variant": {
      "neutral": "radio-neutral",
      "primary": "radio-primary",
      "secondary": "radio-secondary",
      "accent": "radio-accent",
      "info": "radio-info",
      "success": "radio-success",
      "warning": "radio-warning",
      "error": "radio-error"
    },
    "size": {
      "xs": "radio-xs",
      "sm": "radio-sm",
      "md": "radio-md",
      "lg": "radio-lg",
      "xl": "radio-xl"
    },
    "validate": {
      "true": "validator"
    }
  },
  "range": {
    "base": [
      "range"
    ],
    "variant": {
      "neutral": "range-neutral",
      "primary": "range-primary",
      "secondary": "range-secondary",
      "accent": "range-accent",
      "info": "range-info",
      "success": "range-success",
      "warning": "range-warning",
      "error": "range-error"
    },
    "size": {
      "xs": "range-xs",
      "sm": "range-sm",
      "md": "range-md",
      "lg": "range-lg",
      "xl": "range-xl"
    },
    "orientation": {
      "vertical": "range-vertical"
    },
    "validate": {
      "true": "validator"
    }
  },
  "rating": {
    "base": [
      "rating"
    ],
    "shape": {
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
    },
    "variant": {
      "neutral": "bg-neutral",
      "primary": "bg-primary",
      "secondary": "bg-secondary",
      "accent": "bg-accent",
      "info": "bg-info",
      "success": "bg-success",
      "warning": "bg-warning",
      "error": "bg-error"
    },
    "size": {
      "xs": "rating-xs",
      "sm": "rating-sm",
      "md": "rating-md",
      "lg": "rating-lg",
      "xl": "rating-xl"
    },
    "half": {
      "true": "rating-half"
    }
  },
  "select": {
    "base": [
      "select"
    ],
    "variant": {
      "neutral": "select-neutral",
      "primary": "select-primary",
      "secondary": "select-secondary",
      "accent": "select-accent",
      "info": "select-info",
      "success": "select-success",
      "warning": "select-warning",
      "error": "select-error"
    },
    "size": {
      "xs": "select-xs",
      "sm": "select-sm",
      "md": "select-md",
      "lg": "select-lg",
      "xl": "select-xl"
    },
    "ghost": {
      "true": "select-ghost"
    },
    "validate": {
      "true": "validator"
    }
  },
  "skeleton": {
    "base": [
      "skeleton"
    ],
    "text": {
      "true": "skeleton-text"
    }
  },
  "stack": {
    "base": [
      "stack"
    ],
    "direction": {
      "top": "stack-top",
      "bottom": "stack-bottom",
      "start": "stack-start",
      "end": "stack-end"
    }
  },
  "stat.desc": {
    "base": [
      "stat-desc"
    ],
    "variant": {
      "primary": "text-primary",
      "secondary": "text-secondary",
      "accent": "text-accent",
      "neutral": "text-neutral",
      "info": "text-info",
      "success": "text-success",
      "warning": "text-warning",
      "error": "text-error"
    }
  },
  "stat.figure": {
    "base": [
      "stat-figure"
    ],
    "variant": {
      "primary": "text-primary",
      "secondary": "text-secondary",
      "accent": "text-accent",
      "neutral": "text-neutral",
      "info": "text-info",
      "success": "text-success",
      "warning": "text-warning",
      "error": "text-error"
    }
  },
  "stat.group": {
    "base": [
      "stats"
    ],
    "direction": {
      "horizontal": "stats-horizontal",
      "vertical": "stats-vertical"
    }
  },
  "stat.value": {
    "base": [
      "stat-value"
    ],
    "variant": {
      "primary": "text-primary",
      "secondary": "text-secondary",
      "accent": "text-accent",
      "neutral": "text-neutral",
      "info": "text-info",
      "success": "text-success",
      "warning": "text-warning",
      "error": "text-error"
    }
  },
  "status": {
    "base": [
      "status"
    ],
    "variant": {
      "neutral": "status-neutral",
      "primary": "status-primary",
      "secondary": "status-secondary",
      "accent": "status-accent",
      "info": "status-info",
      "success": "status-success",
      "warning": "status-warning",
      "error": "status-error"
    },
    "size": {
      "xs": "status-xs",
      "sm": "status-sm",
      "md": "status-md",
      "lg": "status-lg",
      "xl": "status-xl"
    },
    "animate": {
      "ping": "animate-ping",
      "bounce": "animate-bounce"
    }
  },
  "steps": {
    "base": [
      "steps"
    ],
    "direction": {
      "horizontal": "steps-horizontal",
      "vertical": "steps-vertical"
    }
  },
  "steps.item": {
    "base": [
      "step"
    ],
    "variant": {
      "neutral": "step-neutral",
      "primary": "step-primary",
      "secondary": "step-secondary",
      "accent": "step-accent",
      "info": "step-info",
      "success": "step-success",
      "warning": "step-warning",
      "error": "step-error"
    }
  },
  "swap": {
    "base": [
      "swap"
    ],
    "effect": {
      "rotate": "swap-rotate",
      "flip": "swap-flip"
    }
  },
  "table": {
    "base": [
      "table"
    ],
    "size": {
      "xs": "table-xs",
      "sm": "table-sm",
      "md": "table-md",
      "lg": "table-lg",
      "xl": "table-xl"
    },
    "zebra": {
      "true": "table-zebra"
    },
    "pinRows": {
      "true": "table-pin-rows"
    },
    "pinCols": {
      "true": "table-pin-cols"
    }
  },
  "tabs": {
    "base": [
      "tabs"
    ],
    "style": {
      "border": "tabs-border",
      "lift": "tabs-lift",
      "box": "tabs-box"
    },
    "placement": {
      "bottom": "tabs-bottom"
    },
    "size": {
      "xs": "tabs-xs",
      "sm": "tabs-sm",
      "md": "tabs-md",
      "lg": "tabs-lg",
      "xl": "tabs-xl"
    }
  },
  "tabs.content": {
    "base": [
      "tab-content"
    ],
    "checked": {
      "true": "tab-active"
    },
    "disabled": {
      "true": "tab-disabled"
    }
  },
  "text": {
    "base": [],
    "variant": {
      "neutral": "text-neutral",
      "primary": "text-primary",
      "secondary": "text-secondary",
      "accent": "text-accent",
      "info": "text-info",
      "success": "text-success",
      "warning": "text-warning",
      "error": "text-error"
    },
    "size": {
      "xs": "text-xs",
      "sm": "text-sm",
      "md": "text-base",
      "lg": "text-lg",
      "xl": "text-xl",
      "2xl": "text-2xl",
      "3xl": "text-3xl",
      "4xl": "text-4xl"
    },
    "underline": {
      "true": "underline"
    }
  },
  "textarea": {
    "base": [
      "textarea"
    ],
    "variant": {
      "neutral": "textarea-neutral",
      "primary": "textarea-primary",
      "secondary": "textarea-secondary",
      "accent": "textarea-accent",
      "info": "textarea-info",
      "success": "textarea-success",
      "warning": "textarea-warning",
      "error": "textarea-error"
    },
    "size": {
      "xs": "textarea-xs",
      "sm": "textarea-sm",
      "md": "textarea-md",
      "lg": "textarea-lg",
      "xl": "textarea-xl"
    },
    "ghost": {
      "true": "textarea-ghost"
    },
    "validate": {
      "true": "validator"
    }
  },
  "timeline": {
    "base": [
      "timeline"
    ],
    "direction": {
      "horizontal": "timeline-horizontal",
      "vertical": "timeline-vertical"
    },
    "compact": {
      "true": "timeline-compact"
    },
    "snap": {
      "true": "timeline-snap-icon"
    }
  },
  "timeline.end": {
    "base": [
      "timeline-end"
    ],
    "box": {
      "true": "timeline-box"
    }
  },
  "timeline.item": {
    "base": [],
    "startBox": {
      "true": "timeline-box"
    },
    "endBox": {
      "true": "timeline-box"
    },
    "variant": {
      "neutral": "bg-neutral / text-neutral",
      "primary": "bg-primary / text-primary",
      "secondary": "bg-secondary / text-secondary",
      "accent": "bg-accent / text-accent",
      "info": "bg-info / text-info",
      "success": "bg-success / text-success",
      "warning": "bg-warning / text-warning",
      "error": "bg-error / text-error"
    }
  },
  "timeline.start": {
    "base": [
      "timeline-start"
    ],
    "box": {
      "true": "timeline-box"
    }
  },
  "toast": {
    "base": [
      "toast"
    ],
    "horizontal": {
      "start": "toast-start",
      "center": "toast-center",
      "end": "toast-end"
    },
    "vertical": {
      "top": "toast-top",
      "middle": "toast-middle",
      "bottom": "toast-bottom"
    }
  },
  "toggle": {
    "base": [
      "toggle"
    ],
    "variant": {
      "primary": "toggle-primary",
      "secondary": "toggle-secondary",
      "accent": "toggle-accent",
      "neutral": "toggle-neutral",
      "info": "toggle-info",
      "success": "toggle-success",
      "warning": "toggle-warning",
      "error": "toggle-error"
    },
    "size": {
      "xs": "toggle-xs",
      "sm": "toggle-sm",
      "md": "toggle-md",
      "lg": "toggle-lg",
      "xl": "toggle-xl"
    },
    "validate": {
      "true": "validator"
    }
  },
  "tooltip": {
    "base": [
      "tooltip"
    ],
    "placement": {
      "top": "tooltip-top",
      "bottom": "tooltip-bottom",
      "left": "tooltip-left",
      "right": "tooltip-right"
    },
    "align": {
      "start": "tooltip-start",
      "center": "tooltip-center",
      "end": "tooltip-end"
    },
    "variant": {
      "neutral": "tooltip-neutral",
      "primary": "tooltip-primary",
      "secondary": "tooltip-secondary",
      "accent": "tooltip-accent",
      "info": "tooltip-info",
      "success": "tooltip-success",
      "warning": "tooltip-warning",
      "error": "tooltip-error"
    },
    "open": {
      "true": "tooltip-open"
    }
  },
  "validator.hint": {
    "base": [
      "validator-hint"
    ],
    "hidden": {
      "true": "hidden"
    }
  }
};
window.lb.classes = function(name, props, extra) {
  var schema = window.lb._schemas[name];
  if (!schema) return extra || '';
  var classes = (schema.base || []).slice();
  for (var prop in props) {
    var map = schema[prop];
    if (map && map[props[prop]]) classes.push(map[props[prop]]);
  }
  if (extra) classes.push(extra);
  return classes.filter(Boolean).join(' ');
};
