import modal_form_wrapper from './modals/modal-form-wrapper';
import form_usermessage from './form-usermessage';

const modal_form_usermessage_mixin = {
    components: {
        "modal-form-wrapper": modal_form_wrapper,
        'form-usermessage': form_usermessage
    },
    delimiters: ['[[', ']]'],
    data: {
        form_presets: {
            csrf_token: csrf,
            recipient_id: "",
            recipient_name: "",
            subject: "",
        },
        urls: {
            send_message: "/message/send"
        },
    },
    methods: {
        setFormPresets: function(event){
            let source = event.target
            this.form_presets.recipient_id = source.dataset.id
            this.form_presets.recipient_name = source.dataset.name
            this.form_presets.subject = source.dataset.subject
        },
    },
}
export default modal_form_usermessage_mixin;