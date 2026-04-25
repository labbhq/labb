// stat_figure.js

const statFigureConfig = {
  baseClasses: ["stat-figure"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
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
  }
};

window.lb.createComponent(statFigureConfig, 'lbStatFigureComp', 'stat.figure');
