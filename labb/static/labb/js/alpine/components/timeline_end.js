// timeline_end.js

const timelineEndConfig = {
  baseClasses: ["timeline-end"],
  variables: {
    box: {
        "default": false,
        "css_mapping": {
            "true": "timeline-box"
        }
    },
  }
};

window.lb.createComponent(timelineEndConfig, 'lbTimelineEndComp', 'timeline.end');
