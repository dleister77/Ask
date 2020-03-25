import FormElementMixin from './form-element-mixin';

const FormInput = {
  mixins: [FormElementMixin],
  props: {
    placeholder: {
      type: String,
      required: false,
    },
    type: {
      type: String,
      required: false,
      default: 'text',
    },
  },
  template: `
  <div class="form-group">
      <label
        v-bind:for="name">
        <slot></slot>
      </label>
      <small v-if="!required" class="text-muted font-italic">optional</small>
      <input
        class="form-control"
        :class="error_class"
        v-bind="$props"
        v-bind:id="name"
        v-on:change="updateValue($event.target.value)">
      </input>
      <error-message
          v-if="required"
          :field="validator"
          validator="required">
          <slot></slot> is required.
      </error-message>
      <slot name="errors"></slot>
      <template v-for="error in filtered_server_side_errors">
        <small class="form-error-message">
        [[ error ]]
        </small>
      </template>
  </div>
  `,
};

export default FormInput;
