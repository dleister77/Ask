import ErrorMessage from './error-message';


const FormElementMixin = {
  components: {
    'error-message': ErrorMessage,
  },
  delimiters: ['[[', ']]'],
  props: {
    name: {
      type: String,
      required: true,
    },
    readonly: {
      type: Boolean,
      required: false,
      default: false,
    },
    value: {
      type: String,
      required: false,
      default: '',
    },
    required: {
      type: Boolean,
      required: false,
      default: true,
    },
    validator: {
      type: Object,
      required: false,
    },
    server_side_errors: {
      type: Array,
      required: false,
    },
  },
  computed: {
    has_sse() {
      const notEmptyArray = JSON.stringify(this.server_side_errors) !== JSON.stringify(Array(0))
      const notUndefined = this.server_side_errors !== undefined;
      return notEmptyArray && notUndefined;
    },
    has_vuelidate() {
      return this.validator !== undefined;
    },
    is_invalid() {
      const vuelidateInvalid = this.has_vuelidate && this.validator.$error;
      const sseInvalid = this.has_sse;
      return vuelidateInvalid || sseInvalid;
    },
    filtered_server_side_errors() {
      if (this.has_sse) {
        const errors = this.server_side_errors.filter((error) => {
          return !error.includes('require');
        });
        return errors;
      } return this.server_side_errors;
    },
    error_class() {
      if (this.is_invalid) {
        return 'form-error';
      }
      return '';
    },
  },
  methods: {
    updateValue(value) {
      this.$emit('input', value);
    },
  },
};

export default FormElementMixin;
