// timeline_start.js

const timelineStartConfig = {
  baseClasses: ["timeline-start"],
  variables: {
    box: {
        "default": false,
        "css_mapping": {
            "true": "timeline-box"
        }
    },
  }
};

window.lb.createComponent(timelineStartConfig, 'lbTimelineStartComp', 'timeline.start');
