
let form_input_group = {
    props: {
        name: {
            type: String,
            required: true,
        },
        placeholder: {
            type: String,
            required: false,
        },
        readonly: {
            type: Boolean,
            required: false,
            default: false,
        },
        value: {
            type: String,
            required: false,
            default: "",
        },
        type: {
            type: String,
            required: false,
            default: "text"
        },
        autocompleteUrl: {
            type: String,
            required: false,
        }           
    },
    methods: {
        updateValue: function(value){
            this.$emit('input', value);
        },
    },
    template: `
    <div class="form-group">
        <label
          v-bind:for="name">
          <slot></slot>
        </label>
        <input
          class="form-control"
          v-bind="$props"
          v-bind:id="name"
          v-on:change="updateValue($event.target.value)">
        </input>
    </div>
    `,
}

export default form_input_group;