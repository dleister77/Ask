
const FormWrapperMixin = {
  data() {
    return {
      reset_form_values: false,
      set_form_values: false,
    };
  },
  delimiters: ['[[', ']]'],
  props: {
    form_presets: {
      type: Object,
      required: false,
    },
    url: {
      type: String,
      required: true,
    },
  },
  methods: {
    mark_form_reset() {
      this.reset_form_values = false;
    },
    mark_form_set() {
      this.set_form_values = false;
    },
  },
};

export default FormWrapperMixin;
