// avatar_group.js

const avatarGroupConfig = {
  baseClasses: ["avatar-group"],
  variables: {
    spacing: {
        "default": "tight",
        "css_mapping": {
            "wide": "",
            "normal": "-space-x-2",
            "tight": "-space-x-6",
            "tighter": "-space-x-8",
            "tightest": "-space-x-12"
        }
    },
  }
};

window.lb.createComponent(avatarGroupConfig, 'lbAvatarGroupComp', 'avatar.group');
