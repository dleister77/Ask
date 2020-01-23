
const messageApp = new Vue({
    el: '#messageApp',
    delimiters: ['[[', ']]'],
    components:{
        'message-row': () => import('./components/message-row.js'),
        'message-read': () => import('./components/message-read.js'),
        'pagination-nav': () => import('./components/pagination-nav.js'),
        'form-input-group': () => import('./components/form-input-group.js'),
        'form-textbox-group': () => import('./components/form-textbox-group.js'),
        'folder-nav': () => import('./components/folder-nav.js'),
        'form-input-typeahead': () => import('./components/form-input-typeahead.js'),
    },
    data: {
        active_index: null,
        messages: list,
        csrf: csrf,
        eventSignal: {
            updateActive: "update-active-message",
            newMessage: "new-message",
            backToLast: "back-to-last",
            replyToMessage: "reply-to-message",
            moveMessage: 'move-message',
        },
        newMessage: {
            conversation_id: "",
            recipient_id: "",
            recipient: "",
            subject: "",
            body: "",
        },
        pagination_urls: pagination_urls,
        selectedMessages: [],
        show: {
            newMessage: false,
        },
        urls: links,
    },
    computed: {
        active_message: function(){
            if (0 <= this.active_index  && this.active_index< this.messages.length){
                return this.messages[this.active_index]
            }
        },
        folderIsVisible: function(){
            return !this.is_active && !this.newMessageIsVisible;
        },
        is_active: function(){
            return this.active_index != null;
        },
        messageIsVisible: function(){
            return this.is_active && !this.newMessageIsVisible;
        },
        moveLinksVisible: function(){
            return this.selectedMessages.length > 0
        },
        newMessageIsVisible: function(){
            return this.show.newMessage
        },
    },
    methods: {
        markAsRead: function(){
            let self = this;
            let data = {id: this.active_message.id, csrf_token: this.csrf};
            axios.post(this.urls.updateMessageRead, formDataFromObject(data))
            .then(function(response){
                if (response.data.status == "success"){
                    self.active_message.read = true;
                }
                else {
                    console.log("Error: mark as read failed.")
                }
            })
            .catch(function(error){
                console.log(error);
            })
        },
        moveMessage: function(status){
            let form_data = {
                'message_id': this.selectedMessages.toString(),
                'status': status,
                'csrf_token': this.csrf
            };
            post(this.urls.move, form_data);
        },
        replyToMessage: function(){
            this.newMessage.conversation_id = this.active_message.conversation_id;
            this.newMessage.recipient_id = this.active_message.sender_id;
            this.newMessage.recipient = this.active_message.sender_full_name;
            if (this.active_message.subject.startsWith("Re:")){
                this.newMessage.subject = this.active_message.subject;
            } else {
                this.newMessage.subject = `Re: ${this.active_message.subject}`;
            }
            this.newMessage.body = `\n\nOn ${this.active_message.timestamp}, ${this.active_message.sender_full_name} wrote:\n${this.active_message.body}`
            this.show.newMessage = true;
        },
        reverseMessages: function(){
            this.messages.reverse();
        },
        sendMessage: function(){
            let self = this;
            const f = new FormData(document.getElementById('message-form'));
            axios.post(this.urls.send_message, f)
            .then(function(response){
                if (response.data.status == 'success'){
                    self.show.newMessage = false;
                    alert("Message sent");
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
        },
        showMessage: function(message){
            this.active_index = this.messages.indexOf(message);
            this.selectedMessages.push(message.id);
            if (!message.read){
                this.markAsRead()
            }
        },
        showNewMessage: function(){
            this.show.newMessage = true;
            this.active_index = null;
        },
        showLastPage: function(){
            if (this.messageIsVisible){
                this.active_index = null;
                this.selectedMessages = [];
            } else if (this.newMessageIsVisible && this.active_index != null){
                this.show.newMessage = false;
            } else {
                this.active_index = null;
                this.show.newMessage = false;
            }
        },
        updateActiveMessage: function(adjust){
            if (0 <= this.active_index + adjust < this.messages.length){  
                this.active_index += adjust
            }
        },
        updateSelectedMessages: function(update){
            let [addToSelected, id] = update;
            if (addToSelected){
                this.selectedMessages.push(id);
            } else {
                this.selectedMessages = this.selectedMessages.filter(value => value != id);
            }
        },
        updateRecipientID: function(value){
            this.newMessage.recipient_id = value;
        }
    },
    mounted: function(){
        this.$nextTick();
        console.log(this.$refs);
    }
});

export default messageApp;

