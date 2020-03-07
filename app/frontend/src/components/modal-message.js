import Vue from 'vue';
import Vuelidate from 'vuelidate';

import form_input_group from './form-input-group';
import form_textbox from './form-textbox';
import FormInput from './form-input';


import axios from 'axios';

import required from 'vuelidate/lib/validators/required';

Vue.use(Vuelidate);

let modal_message = {
    components: {
        'form-input': FormInput,
        'form-input-group': form_input_group,
        'form-textbox': form_textbox,
    },
    data: function(){
        return {
            form: {
                recipient_id: this.recipient.id,
                recipient_name: this.recipient.name,
                subject: this.recipient.subject,
                body: "",
            },
        }
    },
    delimiters: ["[[", "]]"],
    props: {
        csrf: {
            type: String,
            required: false,
        },
        recipient: {
            type: Object,
            required: false,
        },
        url: {
            type: String,
            required: true,
        },
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
        resetMessage: function(event) {
            this.$v.$reset();
            Object.keys(this.form).forEach((key)=> this.form[key]="");
        },
        setMessageValues: function() {
            this.form.recipient_name = this.recipient.name;
            this.form.subject = this.recipient.subject;
        },
        sendMessage: function(){
            if (this.$v.$invalid){
                alert("Please correct errors and resubmit")
            } else {
                let self = this;
                const form = new FormData(document.getElementById('message-form'));
                axios.post(this.url, form)
                .then(function(response){
                    if (response.data.status == 'success'){
                        alert("Message sent");
                        self.toggleModal()
                    } else {
                        let message = "Unabled to send message. Please correct errors:\n"
                        message += response.data.errorMsg.join('\n');
                        alert(message);
                    }
                })
                .catch(function(error){
                    console.log(error);
                    alert("Error: Unable to send message.  Please reload and try again.")
                })
            }
        },
        toggleModal: function(){
            this.show = !this.show;
            jQuery('#message-modal').modal('toggle');
        },
    },
    mounted: function(){
        $(this.$refs.vuemodal).on('hide.bs.modal', this.resetMessage);
        $(this.$refs.vuemodal).on('show.bs.modal', this.setMessageValues);
    },
    watch: {
        'recipient.name': function(new_val) {
            this.form.recipient_name = new_val;
        },
        'recipient.subject': function(new_val) {
            this.form.subject = new_val;
        },
    },
    template: `
    <div class="modal fade" ref="vuemodal" id="message-modal" tabindex="-1" role="dialog">
        <div class="modal-dialog modal-md" role="document">
            <div class="modal-content">
                <form id = "message-form" v-bind:action="url" method="POST">
                    <div class="modal-header">
                        <h5 class="modal-title"><slot></slot></h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body px-5">
                        <input v-bind="{name: 'csrf_token', value: csrf, type:'hidden'}">
                        <input v-bind="{name: 'recipient_id', value: recipient.id, type:'hidden'}">
                        
                        <div class="form-group">
                            <form-input
                            name="recipient"
                                v-model.trim="$v.form.recipient_name.$model"
                                :readonly=true
                                :value=recipient.name
                                :validator=$v.form.recipient_name>
                                To
                            </form-input>
                        </div>
                        <div class="form-group">
                            <form-input
                                name='subject'
                                v-model.trim="$v.form.subject.$model"
                                :validator="$v.form.subject"
                                :value=recipient.subject>
                                Subject
                            </form-input>
                        </div>
                        <form-textbox
                            name='body'
                            v-model.trim="$v.form.body.$model"
                            :validator="$v.form.body">
                            Message Body
                        </form-textbox>
                    </div>
                    <div class="modal-footer">
                        <button
                            class="btn btn-primary btn-block submit"
                            type="submit"
                            v-on:click.prevent="sendMessage">
                            Submit
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
    
    `
}

export default modal_message;