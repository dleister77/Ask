/* eslint-disable func-names */
import Vue from 'vue';

import VueSweetalert2 from 'vue-sweetalert2';
import 'sweetalert2/dist/sweetalert2.min.css';
import required from 'vuelidate/lib/validators/required';
import sameAs from 'vuelidate/lib/validators/sameAs';
import maxLength from 'vuelidate/lib/validators/maxLength';
import minLength from 'vuelidate/lib/validators/minLength';
import and from 'vuelidate/lib/validators/and';
import email from 'vuelidate/lib/validators/email';
import { minValue } from 'vuelidate/lib/validators';

import FormMixin from './forms/form_mixin';
import ErrorMessage from './forms/error-message';
import FormInput from './forms/form-input';
import FormInputSelect from './forms/form-input-select';
import { states } from '../../supporting/states';

Vue.use(VueSweetalert2);

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
          required: and(required, minValue(1)),
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
        this.$swal({
          title: 'Unable to Send Message',
          text: 'Please correct errors and resubmit',
          icon: 'error',
        });
        event.preventDefault();
        this.$v.$touch();
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
      <form
        ref="form_ref"
        :id="form_id"
        :action="url"
        method="POST"
        novalidate="true">

          <input type="hidden"
          :value="form.csrf_token"
          name="csrf_token">

          <form-input
            ref="first_name"
            name="first_name"
            v-model.trim="$v.form.first_name.$model"
            :validator="$v.form.first_name"
            :server_side_errors="server_side_errors.first_name">
            <template #default>First Name</template>
          </form-input>

          <form-input
            ref="last_name"
            name="last_name"
            v-model.trim="$v.form.last_name.$model"
            :validator="$v.form.last_name"
            :server_side_errors="server_side_errors.last_name">
            <template #default>Last Name</template>
          </form-input>

          <form-input
            ref="address-line1"
            name="address-line1"
            v-model.trim="$v.form.address.line1.$model"
            :validator="$v.form.address.line1"
            :server_side_errors="server_side_errors.address ? server_side_errors.address.line1 : undefined">
            <template #default>Street Address</template>
          </form-input>

          <form-input
            ref="address-line2"
            name="address-line2"
            :required="false"
            v-model.trim="form.address.line2"
            :server_side_errors="server_side_errors.address ? server_side_errors.address.line2 : undefined">
            <template #default>Address Line 2</template>
          </form-input>

          <form-input
            ref="address-city"
            name="address-city"
            v-model.trim="$v.form.address.city.$model"
            :validator="$v.form.address.city"
            :server_side_errors="server_side_errors.address ? server_side_errors.address.city : undefined">
            <template #default>City</template>
          </form-input>

          <form-input-select
            ref="address-state"
            name="address-state"
            :options="options.states"
            :validator="$v.form.address.state"
            :value="form.address.state"
            v-model="$v.form.address.state.$model"
            :server_side_errors="server_side_errors.address ? server_side_errors.address.state : undefined">
            <template #default>State</template>
          </form-input-select> 

          <form-input
            ref="address-zip"
            name="address-zip"
            v-model.trim="$v.form.address.zip.$model"
            :validator="$v.form.address.zip"
            :server_side_errors="server_side_errors.address ? server_side_errors.address.zip : undefined">
            <template #default>Zip Code</template>
            <template v-slot:errors>
              <error-message
                :field="$v.form.address.zip"
                validator="length">
                Zip code must be 5 characters in length.
              </error-message>
            </template>
          </form-input>

          <form-input
            ref="email"
            name="email"
            v-model.trim="$v.form.email.$model"
            :validator="$v.form.email"
            :server_side_errors="server_side_errors.email">
            <template #default>Email</template>
            <template v-slot:errors>
              <error-message 
                :field="$v.form.email"
                validator="email">
                <template #default>Invalid email address.</template></default>
              </error-message>
            </template>  
          </form-input>

          <form-input
            ref="username"
            name="username"
            v-model.trim="$v.form.username.$model"
            :validator="$v.form.username"
            :server_side_errors="server_side_errors.username">
            <template #default>Username</template>
          </form-input>

          <form-input
            ref="password"
            name="password"
            type="password"
            v-model.trim="$v.form.password.$model"
            :validator="$v.form.password"
            :server_side_errors="server_side_errors.password">
            <template #default>Password</template>
            <template v-slot:errors>
              <error-message 
                :field="$v.form.password"
                validator="between">
                Password must be between 7 & 15 characters in length.
              </error-message>
            </template>    
          </form-input>

          <form-input
            ref="confirmation"
            name="confirmation"
            type="password"
            v-model.trim="$v.form.confirmation.$model"
            :validator="$v.form.confirmation"
            :server_side_errors="form.confirmation.errors">
            <template #default>Confirmation</template>
            <template v-slot:errors>
              <error-message 
                :field="$v.form.confirmation"
                validator="matches">
                Confirmation does not match entered password.
              </error-message>                
            </template>
          </form-input>

          <button
              id="submit"
              type="submit"
              class="btn btn-primary btn-block"
              @click="submit">
              Submit
          </button>             
      </form>
  </div>

  `,
};
export default FormRegister;
