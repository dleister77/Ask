/* eslint-disable no-alert */
/* eslint-disable func-names */
import required from 'vuelidate/lib/validators/required';
import sameAs from 'vuelidate/lib/validators/sameAs';
import maxLength from 'vuelidate/lib/validators/maxLength';
import minLength from 'vuelidate/lib/validators/minLength';
import and from 'vuelidate/lib/validators/and';
import email from 'vuelidate/lib/validators/email';

import FormMixin from './forms/form_mixin';
import ErrorMessage from './forms/error-message';
import FormInput from './forms/form-input';
import FormInputSelect from './forms/form-input-select';
import { states } from '../../supporting/states';


const FormRegister = {
  components: {
    'error-message': ErrorMessage,
    'form-input': FormInput,
    'form-input-select': FormInputSelect,
  },
  mixins: [FormMixin],
  computed: {},
  data() {
    return {
      form: {
        csrf_token: '',
        first_name: '',
        last_name: '',
        address: {
          line1: '',
          line2: '',
          city: '',
          state: 0,
          zip: '',
        },
        email: '',
        username: '',
        password: '',
        confirmation: '',
      },
      options: {
        states,
      },
    };
  },
  delimiters: ['[[', ']]'],
  props: {
    form_errors: {
      type: Object,
      required: true,
    },
  }, // set by mixin
  validations: {
    form: {
      first_name: {
        required,
      },
      last_name: {
        required,
      },
      address: {
        line1: {
          required,
        },
        city: {
          required,
        },
        state: {
          required,
        },
        zip: {
          required,
          length: and(minLength(5), maxLength(5)),
        },
      },
      email: {
        required,
        email,
      },
      username: {
        required,
      },
      password: {
        required,
        between: and(minLength(7), maxLength(15)),
      },
      confirmation: {
        required,
        matches: sameAs(function () {
          return this.form.password;
        }),
      },
    },
  },
  methods: {
    submit(event) {
      if (this.$v.$invalid) {
        alert('Please correct errors and resubmit');
      } else {
        event.target.submit();
      }
    },
  },
  watch: {
    form_errors: {
      handler: function () {
        this.server_side_errors = this.form_errors;
      },
      immediate: true,
      deep: true,
    },
  },
  template: `
  <div>
      <form :id="form_id" :action="url" method="POST">

          <form-input
              v-if="form.contact_info_updated"
              name="email"
              :required="false"
              :validator="$v.form.email"
              v-model="$v.form.email.$model"
              :server_side_errors="server_side_errors.email">
              Email Address
              <template v-slot:errors>
                  <error-message
                  :field="$v.form.email"
                  validator="or">
                  Invalid email address
                  </error-message>
              </template>
          </form-input>

          <input type="hidden"
          :value="form.csrf_token"
          name="csrf_token">

          <form-input
              name="first_name"
              v-model.trim="$v.form.first_name.$model"
              :validator="$v.form.first_name"
              :server_side_errors="server_side_errors.first_name">
              First Name
          </form-input>

          <form-input
              name="last_name"
              v-model.trim="$v.form.last_name.$model"
              :validator="$v.form.last_name"
              :server_side_errors="server_side_errors.last_name">
              Last Name
          </form-input>

          <form-input
              name="address-line1"
              v-model.trim="$v.form.address.line1.$model"
              :validator="$v.form.address.line1"
              :server_side_errors="server_side_errors.address.line1">
              Street Address
          </form-input>

          <form-input
              name="address-line2"
              :required="false"
              v-model.trim="form.address.line2"
              :server_side_errors="server_side_errors.address.line2">
              Address Line 2
          </form-input>

          <form-input
              name="address-city"
              v-model.trim="$v.form.address.city.$model"
              :validator="$v.form.address.city"
              :server_side_errors="server_side_errors.address.city">
              City
          </form-input>

          <div class="form-group">
              <form-input-select
              name="address-state"
              :options="options.states"
              :validator="$v.form.address.state"
              :value="form.address.state"
              v-model="$v.form.address.state.$model"
              :server_side_errors="server_side_errors.state">
              State
              </form-input-select>
          </div>        

          <form-input
              name="address-zip"
              v-model.trim="$v.form.address.zip.$model"
              :validator="$v.form.address.zip"
              :server_side_errors="server_side_errors.zip">
              Zip Code
              <template v-slot:errors>
                  <error-message
                      :field="$v.form.address.zip"
                      validator="length">
                      Zip code must be 5 characters in length.
                  </error-message>
              </template>
          </form-input>

          <form-input
              name="email"
              v-model.trim="$v.form.email.$model"
              :validator="$v.form.email"
              :server_side_errors="server_side_errors.email">
              Email
              <template v-slot:errors>
                  <error-message 
                      :field="$v.form.email"
                      validator="email">
                      Invalid email address.
                  </error-message>
              </template>  
          </form-input>

          <form-input
              name="username"
              v-model.trim="$v.form.username.$model"
              :validator="$v.form.username"
              :server_side_errors="server_side_errors.username">
              Username
          </form-input>

          <form-input
              name="password"
              type="password"
              v-model.trim="$v.form.password.$model"
              :validator="$v.form.password"
              :server_side_errors="server_side_errors.password">
              Password
              <template v-slot:errors>
                  <error-message 
                      :field="$v.form.password"
                      validator="between">
                      Password must be between 7 & 15 characters in length.
                  </error-message>
              </template>    
          </form-input>

          <form-input
              name="confirmation"
              type="password"
              v-model.trim="$v.form.confirmation.$model"
              :validator="$v.form.confirmation"
              :server_side_errors="form.confirmation.errors">
              Confirmation
              <template v-slot:errors>
                  <error-message 
                      :field="$v.form.confirmation"
                      validator="matches">
                      Confirmation does not match entered password.
                  </error-message>                
              </template>
          </form-input>

          <button
              type="submit"
              class="btn btn-primary btn-block"
              @click="$v.$touch">
              Submit
          </button>             
      </form>
  </div>

  `,
};
export default FormRegister;
