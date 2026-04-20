// chat_bubble.js

const chatBubbleConfig = {
  baseClasses: ["chat-bubble"],
  variables: {
    variant: {
        "default": "",
        "css_mapping": {
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
  }
};

window.lb.createComponent(chatBubbleConfig, 'lbChatBubbleComp', 'chat.bubble');
