import Vue from 'vue';
import Vuelidate from 'vuelidate';
import axios from 'axios';

import {reset_form, set_form} from '../../scripts/forms';

Vue.use(Vuelidate);

let form_mixin = {
    computed: {},
    data: function(){
        return {
            form: {},
            options: {},
            server_side_errors: {},
        }
    },
    delimiters: ["[[", "]]"],
    props: {
        form_id: {
            type: String,
            required: false,
            default: "vue-form",
        },
        form_presets: {
            type: Object,
            required: false,
        },
        url: {
            type: String,
            required: false,
        },
        reset_form_values: {
            type: Boolean,
            required: false,
        },
        set_form_values: {
            type: Boolean,
            required: false,
        },
    },
    validations: {
        form: {},
    },
    methods: {
        populate_form: function() {
            return new FormData(document.getElementById(this.form_id))
        },
        reset_form: function() {
            this.$v.$reset();
            this.form = reset_form(this.form);
            this.$emit('form_is_reset');
        },
        set_form: function() {
            this.form = set_form(this.form_presets, this.form);
            this.$emit('form_is_set');
        },
        submit: async function() {
            this.$emit('form_is_submitted')
            if (this.$v.$invalid){
                alert("Please correct errors and resubmit")
            } else {
                this.server_side_errors = {};
                let self = this;
                const form = this.populate_form();
                axios.post(this.url, form)
                .then(function(response){
                    alert("Message sent");
                    self.$emit('form_is_submitted');
                    self.reset_form();
                })
                .catch(function(error){
                    console.log(error);
                    let message = "Unable to send message. Please correct errors:\n"
                    let form_errors = error.response.data.errors
                    self.server_side_errors = form_errors
                    let displayed_errors = Object.values(form_errors)
                    message += displayed_errors.join('\n');
                    alert(message);
                })
            }
        },
    },
    watch: {
        'set_form_values': function(new_val) {
            if (new_val == true){
                this.set_form();
                this.$emit('form_is_set');
            }
        },
        'reset_form_values': function(new_val) {
            if (new_val==true) {
                this.reset_form();
                this.$emit('form_is_reset')
            }
        },
    },
}
export default form_mixin;