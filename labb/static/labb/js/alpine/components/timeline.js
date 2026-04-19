// timeline.js

const timelineConfig = {
  baseClasses: ["timeline"],
  variables: {
    direction: {
        "default": "",
        "css_mapping": {
            "horizontal": "timeline-horizontal",
            "vertical": "timeline-vertical"
        }
    },
    compact: {
        "default": false,
        "css_mapping": {
            "true": "timeline-compact"
        }
    },
    snap: {
        "default": false,
        "css_mapping": {
            "true": "timeline-snap-icon"
        }
    },
  }
};

window.lb.createComponent(timelineConfig, 'lbTimelineComp', 'timeline');
