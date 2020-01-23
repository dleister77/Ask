let form_textbox_group = {
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
            required: false,
            default: "",
        },
        rows: {
            type: Number,
            required: false,
            default: 6,
        }
    },
    methods: {
        updateValue: function(value){
            this.$emit('input', value);
        }   
    },
    template: `
    <div class="form-group">
        <label
          v-bind:for="name">
          <slot></slot>
        </label>
        <textarea
          class="form-control"
          v-bind="$props"
          v-bind:id="name"
          v-on:change="updateValue($event.target.value)">
        </textarea>
    </div>
    `
};

export default form_textbox_group;
