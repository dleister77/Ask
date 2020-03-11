import ErrorMessage from "./error-message";

let FormInputCheckbox = {
    components: {
        'error-message': ErrorMessage,
    },
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
            type: Boolean,
            required: false,
            default: false,
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
        }
    },
    computed: {
      filtered_server_side_errors() {
        if (this.value != "" && this.server_side_errors != undefined){
          let errors = this.server_side_errors.filter(function(error){
            return !error.includes("require")
          });
          return errors;
        } else {
          return this.server_side_errors;
        }
      },
      error_class: function() {
        if (this.validator != undefined && this.validator.$error){
          return 'form-error'
        }
      }
    },
    methods: {
        updateValue: function(value){
            this.$emit('input', value);
        },
    },
    template: `
    <div class="form-group">
    <div class="form-check">
      <input
        type="checkbox"
        class="form-check-input"
        :class="error_class"
        :checked="value"
        v-bind="$props"
        v-bind:id="name"
        v-on:change="updateValue($event.target.checked)">
      </input>
      <label
        :for="name"
        class="form-check-label">
        <slot></slot>
      </label>
      <small v-if="!required" class="text-muted font-italic">optional</small>

      <error-message
          v-if="required"
          :field="validator"
          validator="required">
          <slot></slot> is required.

      </error-message>
          <template v-for="error in filtered_server_side_errors">
            <small class="form-error-message">
            {{ error }}
            </small>
          </template>

      <slot name="errors"></slot>
    </div>
    </div>
    `,
}

export default FormInputCheckbox;