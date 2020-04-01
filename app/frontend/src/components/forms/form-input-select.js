import FormElementMixin from './form-element-mixin';

const FormInputSelect = {
  mixins: [FormElementMixin],
  computed: {
    options_start_at_0() {
      const firstId = this.options[0].id;
      return firstId === 0;
    },
  },
  data() {
    return {
      selected: '',
    };
  },
  props: {
    value: {
      type: Number,
      required: true,
    },
    options: {
      type: Array,
      required: true,
    },
  },
  // created() {
  //   // this.selected = this.value;
  // },
  // watch: {
  //   selected(value) {
  //     this.$emit('input', value);
  //   },
  // },
  template: `
  <div class="form-group">
      <label
        v-bind:for="name">
        <slot></slot>
      </label>
      <small v-if="!required" class="text-muted font-italic">optional</small>
      <select
        class="form-control"
        :class="{'form-error':validator.$error}"
        v-bind="$props"
        v-bind:id="name"
        :value="value"
        @change=updateValue($event.target.value)>
        <option
          v-if="options[0].id != 0"
          disabled
          value=0><-- Select from list --></option>
        <template v-for="option in options">
          <option 
              :value="option.id">
              [[ option.name ]]
          </option>
        </template>
      </select>
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

export default FormInputSelect;
