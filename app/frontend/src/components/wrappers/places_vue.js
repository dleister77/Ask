import places from 'places.js';

const places = {
  props: {
    container_id: {
      type: String,
      required: true,
    },
    type: {
      type: String,
      required: false,
    },
    api_key: {
      type: String,
      required: true,
    },
    app_id: {
      type: String,
      required: true,
    },
    value: {
      type:String,
      default: '',
    },
  },
  computed: {
    options() {
      return {
        container: document.getElementById(this.container_id),
        appId: this.app_id,
        apiKey: this.api_key,
        type: this.type,
      }
    }
  },
  data() {
    return {
      placesAutocomplete: null,
    };
  },
  watch: {
    options: {
      deep: true,
      handler(newOptions) {
        this.placesAutocomplete.configure(newOptions);
      },
    },
  },
  mounted() {
    this.init();
  },
  methods: {
    init() {
      this.placesAutocomplete = places(this.options);

      this.placesAutocomplete.on('change', e => {
        this.$emit('change', e);
      });
    }
  }
};

export default places;