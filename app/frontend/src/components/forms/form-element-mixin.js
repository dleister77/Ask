import ErrorMessage from "./error-message";

let sse_empty_vals = [undefined, [] ]

let form_element_mixin = {
    components: {
        'error-message': ErrorMessage,
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
        value: {
            type: String,
            required: false,
            default: "",
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
      has_sse: function() {
        let not_empty_array = JSON.stringify(this.server_side_errors) != JSON.stringify(Array(0))
        let not_undefined = this.server_side_errors != undefined
        return not_empty_array && not_undefined;
      },
      has_vuelidate: function() {
        return this.validator != undefined;
      },
      is_invalid: function() {
        let vuelidate_invalid = this.has_vuelidate && this.validator.$error
        let sse_invalid = this.has_sse
        return vuelidate_invalid || sse_invalid;
      },
      filtered_server_side_errors() {
        if (this.has_sse){
          let errors = this.server_side_errors.filter(function(error){
            return !error.includes("require")
          });
          return errors;
        } else {
          return this.server_side_errors;
        }
      },
      error_class: function() {
        let validator_invalid = this.validator != undefined && this.validator.$error;
        let server_side_invalid = !(sse_empty_vals.includes(this.server_side_errors))
        if (this.is_invalid){
          return 'form-error'
        }
      }
    },
    methods: {
        updateValue: function(value){
            this.$emit('input', value);
        },
    },
}

export default form_element_mixin;