import Vue from 'vue';
import Vuelidate from 'vuelidate';

import ErrorMessage from '../../components/error-message';
import FormInput from '../../components/form-input';
import FormInputSelect from '../../components/form-input-select';
import {states} from '../../../supporting/states';


import required from 'vuelidate/lib/validators/required';
import sameAs from 'vuelidate/lib/validators/sameAs';
import between from 'vuelidate/lib/validators/between';
import maxLength from 'vuelidate/lib/validators/maxLength';
import minLength from 'vuelidate/lib/validators/minLength';
import and from 'vuelidate/lib/validators/and'
import { helpers } from 'vuelidate/lib/validators'
import email from 'vuelidate/lib/validators/email'


Vue.use(Vuelidate);


const register = new Vue({
    el: '#app',
    components: {
        'error-message': ErrorMessage,
        'form-input': FormInput,
        'form-input-select': FormInputSelect,
    },
    delimiters: ['[[', ']]'],
    data: {
        form: {
            csrf_token: server_form.csrf_token.value, 
            first_name: {
                value: server_form.first_name.data,
                errors: server_form.first_name.errors,
            },
            last_name: {
                value:server_form.last_name.data,
                errors: server_form.last_name.errors,
            },
            address: {
                line1: {
                    value: server_form.address.line1.data,
                    errors: server_form.address.line1.errors
                },
                line2: {
                    value: server_form.address.line2.data,
                    errors: server_form.address.line2.errors,
                },
                city: {
                    value: server_form.address.city.data,
                    errors: server_form.address.city.errors,
                },
                state: {
                    value: server_form.address.state.data,
                    errors: server_form.address.state.errors
                },
                zip: {
                    value: server_form.address.zip.data,
                    errors: server_form.address.zip.errors,
                },
            },
            email: {
                value: server_form.email.data,
                errors: server_form.email.errors,
            },
            username: {
                value: server_form.username.data,
                errors: server_form.username.errors,
            },
            password: {
                value: server_form.password.data,
                errors: server_form.password.errors,
            },
            confirmation: {
                value: server_form.confirmation.data,
                errors: server_form.confirmation.errors,
            },
        },
        states: states,
    },
    validations: {
        form: {
            first_name: {
                value: {
                    required,
                },
            },
            last_name: {
                value: {
                    required,
                },
            },
            address: {
                line1: {
                    value: {
                        required,
                    },
                },
                city: {
                    value: {
                        required,
                    },
                },
                state: {
                    value: {
                        required,
                    },
                },
                zip: {
                    value: {
                        required,
                        length: and(minLength(5), maxLength(5)),
                    },
                },
            },
            email: {
                value: {
                    required,
                    email,
                },
            },
            username: {
                value: {
                    required,
                },
            },
            password: {
                value: {
                    required,
                    between: and(minLength(7), maxLength(15)),
                },
            },
            confirmation: {
                value: {
                    required,
                    matches: sameAs(function() {
                        return this.form.password.value;
                    }),
                },
            },
        },
    },
    methods: {
        submit: function(event) {
            if (this.$v.$invalid){
                alert("Please correct errors and resubmit")
            } else {
                event.target.submit()
            }
        }
    },
});

export default register;