// kbd.js

const kbdConfig = {
  baseClasses: ["kbd"],
  variables: {
    size: {
        "default": "md",
        "css_mapping": {
            "xs": "kbd-xs",
            "sm": "kbd-sm",
            "md": "kbd-md",
            "lg": "kbd-lg",
            "xl": "kbd-xl"
        }
    },
    variant: {
        "default": "",
        "css_mapping": {
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
  }
};

window.lb.createComponent(kbdConfig, 'lbKbdComp', 'kbd');
