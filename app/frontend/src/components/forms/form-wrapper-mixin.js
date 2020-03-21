

let form_wrapper_mixin = {

    data: function(){
        return {
            reset_form_values: false,
            set_form_values: false,
        }
    },
    delimiters: ["[[", "]]"],
    props: {
        form_presets: {
            type: Object,
            required: false,
        },
        url: {
            type: String,
            required: true,
        },
    },
    methods: {
        mark_form_reset: function() {
            this.reset_form_values = false;
        },
        mark_form_set: function() {
            this.set_form_values = false;
        },
    },
}

export default form_wrapper_mixin;