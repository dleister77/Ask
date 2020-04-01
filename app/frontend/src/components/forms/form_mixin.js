import Vue from 'vue';
import Vuelidate from 'vuelidate';
import axios from 'axios';

import { resetForm, setForm } from '../../scripts/forms';

Vue.use(Vuelidate);

const FormMixin = {
  computed: {},
  data() {
    return {
      form: {},
      options: {},
      server_side_errors: {},
    };
  },
  delimiters: ['[[', ']]'],
  props: {
    form_id: {
      type: String,
      required: false,
      default: 'vue-form',
    },
    form_presets: {
      type: Object,
      required: false,
    },
    url: {
      type: String,
      required: false,
    },
    reset_form_values: {
      type: Boolean,
      required: false,
    },
    set_form_values: {
      type: Boolean,
      required: false,
    },
  },
  validations: {
    form: {},
  },
  methods: {
    populate_form() {
      return new FormData(this.$refs.form_ref);
    },
    reset_form() {
      this.$v.$reset();
      this.server_side_errors = {};
      this.form = resetForm(this.form);
      this.$emit('form_is_reset');
    },
    set_form() {
      this.form = setForm(this.form_presets, this.form);
      this.$emit('form_is_set');
    },
    submit() {
      if (this.$v.$invalid) {
        alert('Please correct errors and resubmit');
      } else {
        this.server_side_errors = {};
        const form = this.populate_form();
        axios.post(this.url, form)
          .then(() => {
            alert('Message sent');
            this.$emit('form_is_submitted');
            this.reset_form();
          })
          .catch((error) => {
            console.log(error);
            let message = 'Unable to send message. Please correct errors:\n';
            const formErrors = error.response.data.errors;
            this.server_side_errors = formErrors;
            if (formErrors !== undefined) {
              const displayedErrors = Object.values(formErrors);
              message += displayedErrors.join('\n');
            }
            alert(message);
          });
      }
    },
  },
  watch: {
    set_form_values(newVal) {
      if (newVal === true) {
        this.set_form();
        this.$emit('form_is_set');
      }
    },
    reset_form_values(newVal) {
      if (newVal === true) {
        this.reset_form();
        this.$emit('form_is_reset');
      }
    },
  },
};
export default FormMixin;
