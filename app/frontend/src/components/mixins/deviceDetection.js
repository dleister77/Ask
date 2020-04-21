const DeviceDetectionMixin = {
  data: {
    windowSize: window.innerWidth,
    isTouchScreen: navigator.maxTouchPoints > 0,
  },
  computed: {
    viewportSize() {
      return this.calcViewPortSize();
    },
    isMobile() {
      const isSmallScreen = this.windowSize < 768;
      return isSmallScreen && this.isTouchScreen;
    },
  },
  methods: {
    calcViewPortSize() {
      const width = this.windowSize;
      let size = '';
      switch (true) {
        case (width > 1200):
          size = 'xl';
          break;
        case (width > 992):
          size = 'lg';
          break;
        case (width > 768):
          size = 'md';
          break;
        case (width > 576):
          size = 'sm';
          break;
        default:
          size = 'xs';
          break;
      }
      return size;
    },
  },
  mounted() {
    window.addEventListener('resize', () => {
      this.windowSize = window.innerWidth;
      this.isTouchScreen = navigator.maxTouchPoints !== undefined ? navigator.maxTouchPoints > 0 : false;
    });
  },
};

export default DeviceDetectionMixin;
