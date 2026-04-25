// modal_box.js

const modalBoxConfig = {
  baseClasses: ["modal-box"],
  variables: {
    size: {
        "default": "",
        "css_mapping": {
            "xs": "w-11/12 sm:w-72 max-w-xs",
            "sm": "w-11/12 sm:w-80 max-w-sm",
            "md": "w-11/12 sm:w-96 max-w-md",
            "lg": "w-11/12 sm:w-[32rem] max-w-lg",
            "xl": "w-11/12 sm:w-[36rem] max-w-xl",
            "screen": "w-11/12 max-w-5xl"
        }
    },
  }
};

window.lb.createComponent(modalBoxConfig, 'lbModalBoxComp', 'modal.box');
