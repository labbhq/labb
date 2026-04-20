// chat_image.js

const chatImageConfig = {
  baseClasses: ["chat-image", "avatar"],
  variables: {
    size: {
        "default": "md",
        "css_mapping": {
            "sm": "w-8",
            "md": "w-10",
            "lg": "w-12"
        }
    },
  }
};

window.lb.createComponent(chatImageConfig, 'lbChatImageComp', 'chat.image');
