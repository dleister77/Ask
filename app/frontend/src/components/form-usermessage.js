import required from 'vuelidate/lib/validators/required';

import FormMixin from './forms/form_mixin';
import FormTextbox from './forms/form-textbox';
import FormInput from './forms/form-input';


const FormUsermessage = {
  components: {
    'form-input': FormInput,
    'form-textbox': FormTextbox,
  },
  mixins: [FormMixin],
  data() {
    return {
      form: {
        csrf_token: '',
        recipient_id: '',
        recipient_name: '',
        subject: '',
        body: '',
      },
    };
  },
  delimiters: ['[[', ']]'],
  props: {}, // set by mixin
  validations: {
    form: {
      recipient_id: {
        required,
      },
      recipient_name: {
        required,
      },
      subject: {
        required,
      },
      body: {
        required,
      },
    },
  },
  methods: {},
  watch: {},
  template: `
  <div>
      <form :id="form_id" :action="url" method="POST">
          <input name="csrf_token" type="hidden" :value="form_presets.csrf_token">
          <input name='recipient_id' type="hidden" :value="form_presets.recipient_id">
              <form-input
                  name="recipient"
                  v-model="$v.form.recipient_name.$model"
                  :readonly=true
                  :validator=$v.form.recipient_name
                  :server_side_errors="server_side_errors.recipient_name">
                  To
              </form-input>
              <form-input
                  name='subject'
                  v-model.trim="$v.form.subject.$model"
                  :validator="$v.form.subject"
                  :server_side_errors="server_side_errors.subject">
                  Subject
              </form-input>
              <form-textbox
                  name='body'
                  v-model.trim="$v.form.body.$model"
                  :validator="$v.form.body"
                  :server_side_errors="server_side_errors.body">
                  Message Body
              </form-textbox>

              <button
                  :id="form_id + '_submit'"
                  class="btn btn-primary btn-block submit"
                  type="submit"
                  v-on:click.prevent="submit">
                  Submit
              </button>
      </form>
  </div>
  
  `,
};
export default FormUsermessage;
