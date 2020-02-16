import Vue from 'vue';
import Vuelidate from 'vuelidate';

import required from 'vuelidate/lib/validators/required';
import sameAs from 'vuelidate/lib/validators/sameAs';

Vue.use(Vuelidate);


const register = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {
        form: {
            password: "",
            confirmation: "",
        }
    },
    validations: {
        form: {
            password: {
                required,
            },
            confirmation: {
                required,
                matches: sameAs('password'),
            },
        }
    },
    methods: {

    },

});

export default register;