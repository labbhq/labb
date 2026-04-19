// timeline_item.js

const timelineItemConfig = {
  baseClasses: [],
  variables: {
    startBox: {
        "default": false,
        "css_mapping": {
            "true": "timeline-box"
        }
    },
    endBox: {
        "default": false,
        "css_mapping": {
            "true": "timeline-box"
        }
    },
    variant: {
        "default": "",
        "css_mapping": {
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
  }
};

window.lb.createComponent(timelineItemConfig, 'lbTimelineItemComp', 'timeline.item');
