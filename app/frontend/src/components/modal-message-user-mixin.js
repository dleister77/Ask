import modal_message_user from './modal-message-user';


const modal_message_user_mixin = {
    components: {
        "modal-message-user": modal_message_user,
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
        setMessagePresets: function(event){
            let source = event.target
            this.form_presets.recipient_id = source.dataset.id
            this.form_presets.recipient_name = source.dataset.name
            this.form_presets.subject = source.dataset.subject
        },
        resetFormPresets: function() {
            Object.keys(this.form_presets).forEach(function(key) {
                if (key != "csrf_token"){
                    this.form_presets[key] = "";
                }
            }, this);
        }
    },
}
export default modal_message_user_mixin;