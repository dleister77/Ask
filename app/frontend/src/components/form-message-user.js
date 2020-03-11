import Vue from 'vue';
import Vuelidate from 'vuelidate';

import form_input_group from './form-input-group';
import form_textbox from './form-textbox';
import FormInput from './form-input';

import required from 'vuelidate/lib/validators/required';

Vue.use(Vuelidate);

let form_message_user = {
    components: {
        'form-input': FormInput,
        'form-input-group': form_input_group,
        'form-textbox': form_textbox,
    },
    data: function(){
        return {
            form: {
                csrf_token: "",
                recipient_id: "",
                recipient_name: "",
                subject: "",
                body: "",
            },
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
        reset_form: {
            type: Boolean,
            required: false,
        }
    },
    validations: {
        form: {
            recipient_id: {
                required,
            },
            recipient_name: {
                required,
            },
            subject: {
                required,
            },
            body: {
                required,
            }
        },
    },
    methods: {
        resetForm: function() {
            this.$v.$reset();
            Object.keys(this.form).forEach((key)=> this.form[key]="");
        },
    },
    watch: {
        'form_presets': {
            handler: function(new_val) {
            Object.entries(this.form_presets).forEach(([key,value])=>this.form[key]=value);
            },
            deep: true,
        },
        'reset_form': function(new_val) {
            if (new_val==true) {
                this.resetForm();
                this.$emit('form_is_reset')
            }
        },
        '$v.$invalid': function(new_val) {
            let is_valid = !new_val;
            this.$emit('form_is_valid', is_valid);
        }        
    },
    template: `
    <div>
        <form id = "message-form" v-bind:action="url" method="POST">
            <input name="csrf_token" type="hidden" :value="form_presets.csrf_token">
            <input name='recipient_id' type="hidden" :value="form_presets.recipient_id">
            <div class="form-group">
                <form-input
                name="recipient"
                    v-model.trim="$v.form.recipient_name.$model"
                    :readonly=true
                    :validator=$v.form.recipient_name>
                    To
                </form-input>
            </div>
            <div class="form-group">
                <form-input
                    name='subject'
                    v-model.trim="$v.form.subject.$model"
                    :validator="$v.form.subject">
                    Subject
                </form-input>
            </div>
            <div class="form-group">
                <form-textbox
                    name='body'
                    v-model.trim="$v.form.body.$model"
                    :validator="$v.form.body">
                    Message Body
                </form-textbox>
            </div>
        </form>
    </div>
    
    `
}
export default form_message_user;