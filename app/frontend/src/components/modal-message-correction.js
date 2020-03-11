import modal_mixin from './modal-mixin';
import form_message_correction from './form-message-correction';

import axios from 'axios';


let modal_message = {
    components: {
        'form-message-correction': form_message_correction,
    },
    mixins: [modal_mixin],
    data: function(){
        return {
            reset_form: false,
            form_is_valid: false,
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
        resetFormPresets: function() {
            this.reset_form = false;
            this.$emit('reset_form_presets');
        },
        setValidity: function(form_is_valid_payload) {
            this.form_is_valid = form_is_valid_payload;
        },
        sendMessage: function(){
            if (!this.form_is_valid){
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
    },
    template: `
    <div>
        <modal
            title="Suggest a Correction"
            :modal_id="modal_id"
            @modal_hide="reset_form=true">
            <template v-slot:body>
                <form-message-correction
                    :form_presets="form_presets"
                    :url="url"
                    :reset_form="reset_form"
                    @form_is_reset="resetFormPresets"
                    @form_is_valid="setValidity">
                </form-message-correction>
            </template>
            <template v-slot:footer>           
                <button
                    class="btn btn-primary btn-block submit"
                    type="submit"
                    v-on:click.prevent="sendMessage">
                    Submit
                </button>
            </template>
        </modal>
    </div>
    
    `
}

export default modal_message;