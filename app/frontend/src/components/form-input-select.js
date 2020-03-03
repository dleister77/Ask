import ErrorMessage from "./error-message";

let FormInputSelect = {
    components: {
        'error-message': ErrorMessage,
    },
    data: function(){
      return {
        selected: "",
      }
    },
    delimiters: [ '[[', ']]'],
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
        required: {
            type: Boolean,
            required: false,
            default: true,
        },
        validator: {
            type: Object,
            required: false,
        },
        value: {
          type: Number,
          required: true,
        },
        options: {
            type: Array,
            required: true,
        },
    },
    mounted: function(){
      this.selected = this.value;
    },
    watch: {
      selected: function(value){
        this.$emit('input', parseInt(value, 10));
      },
    },
    template: `
    <div>
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
    </div>
    `,
}

export default FormInputSelect;