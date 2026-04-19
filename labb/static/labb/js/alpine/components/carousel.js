// carousel.js

const carouselConfig = {
  baseClasses: ["carousel"],
  variables: {
    snap: {
        "default": "start",
        "css_mapping": {
            "start": "carousel-start",
            "center": "carousel-center",
            "end": "carousel-end"
        }
    },
    direction: {
        "default": "horizontal",
        "css_mapping": {
            "horizontal": "",
            "vertical": "carousel-vertical"
        }
    },
  }
};

window.lb.createComponent(carouselConfig, 'lbCarouselComp', 'carousel');
