// chat.js

const chatConfig = {
  baseClasses: ["chat"],
  variables: {
    placement: {
        "default": "start",
        "css_mapping": {
            "start": "chat-start",
            "end": "chat-end"
        }
    },
  }
};

window.lb.createComponent(chatConfig, 'lbChatComp', 'chat');
