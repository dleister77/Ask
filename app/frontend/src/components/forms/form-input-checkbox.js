import form_element_mixin from './form-element-mixin'

let FormInputCheckbox = {
    mixins: [form_element_mixin],
    props: {
      value: {
        type: Boolean,
        required: false,
        default: "",
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
            [[ error ]]
            </small>
          </template>

      <slot name="errors"></slot>
    </div>
    </div>
    `,
}

export default FormInputCheckbox;