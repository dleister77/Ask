import FormElementMixin from './form-element-mixin'

const FormInputSelectMultiple = {
  mixins: [FormElementMixin],
  data() {
    return {
      selected: '',
    };
  },
  props: {
    value: {
      type: Array,
      required: true,
    },
    options: {
      type: Array,
      required: true,
    },
  },
  mounted() {
    this.selected = this.value;
  },
  watch: {
    selected(value) {
      this.$emit('input', value);
    },
  },
  template: `
  <div class="form-group">
      <label
        v-bind:for="name">
        <slot></slot>
      </label>
      <small v-if="!required" class="text-muted font-italic">optional</small>
      <select
        multiple
        class="form-control"
        :class="{'form-error':validator.$error}"
        v-bind="$props"
        v-bind:id="name"
        v-model="selected">
        <option :value="null" selected>Choose from list</option>
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
          <slot></slot>is required.
      </error-message>
      <slot name="errors"></slot>
  </div>
  `,
}

export default FormInputSelectMultiple;