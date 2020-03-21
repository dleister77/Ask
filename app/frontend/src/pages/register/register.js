import Vue from 'vue';

import form_register from '../../components/form-register';

const register = new Vue({
    el: '#app',
    components: {
        'form-register': form_register,
    },
    delimiters: ['[[', ']]'],
    data: {
        form_presets: {
            csrf_token: form_values.csrf_token,
            first_name: form_values.first_name,
            last_name: form_values.last_name,
            address: {
                line1: form_values.address.line1,
                line2: form_values.address.line2,
                city: form_values.address.city,
                state: form_values.address.state,
                zip: form_values.address.zip,
            },
            email: form_values.email,
            username: form_values.username,
            password: "",
            confirmation: "",
        },
        form_errors: form_errors,
        set_form_values: false,
        urls: {
            register: urls.register,
        }
    },
    methods: {
        mark_form_set: function() {
            this.set_form_values = false;
        }
    },
    mounted: function() {
        this.set_form_values = true;
    }
});

export default register;