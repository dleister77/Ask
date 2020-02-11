
let form_input_typeahead = {
    components:{
        'typeahead': () => import('./typeahead.js'),
    },
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
        url: {
            type: String,
            required: false,
        }           
    },
    methods: {
        updateValue: function(value){
            this.$emit('input', value);
        },
        emitMessage: function(msg){
            this.$emit(msg.name, msg.value)
        }
    },
    template: `
    <div class="form-group">
        <label
          v-bind:for="name">
          <slot></slot>
        </label>
        <typeahead
          v-bind:url="url"
          v-bind="$props"
          v-bind:id="name"
          v-on:input="updateValue"
          v-on:id-change="emitMessage"/>
        </input>
    </div>
    `,
}

export default form_input_typeahead;