import form_element_mixin from './form-element-mixin'

let FormInputSelect = {
    mixins: [form_element_mixin],
    computed: {
      options_start_at_0: function() {
        return this.options[0].id == 0;
      }
    },
    data: function(){
      return {
        selected: "",
      }
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
    mounted: function(){
      this.selected = this.value;
    },
    watch: {
      selected: function(value){
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
          class="form-control"
          :class="{'form-error':validator.$error}"
          v-bind="$props"
          v-bind:id="name"
          v-model="selected">
          <option
            v-if="options[0].id != 0"
            value=0>
            <-- Select from list -->
          </option>
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
        <template v-for="error in filtered_server_side_errors">
        <small class="form-error-message">
        [[ error ]]
        </small>
      </template>
    </div>
    `,
}

export default FormInputSelect;