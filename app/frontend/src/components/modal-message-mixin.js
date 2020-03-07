import modal_message from './modal-message';


const modal_message_mixin = {
    components: {
        "modal-message": modal_message,
    },
    delimiters: ['[[', ']]'],
    data: {
        recipient: {
            id: "",
            name: "",
            subject: "",
        },
        urls: {
            send_message: "/message/send"
        },
        csrf: csrf,
    },
    methods: {
        setRecipient: function(event){
            let source = event.target
            this.recipient.id = source.dataset.id
            this.recipient.name = source.dataset.name
            this.recipient.subject = source.dataset.subject
        }

    },
}
export default modal_message_mixin;