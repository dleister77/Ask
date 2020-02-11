import Vue from 'vue';
import message_row from '../../components/message-row';
import message_read from '../../components/message-read';
import pagination_nav from '../../components/pagination-nav';
import form_input_group from '../../components/form-input-group';
import form_textbook_group from '../../components/form-textbox-group';
import folder_nav from '../../components/folder-nav';
import VueBootstrapTypeahead from 'VueBootstrapTypeahead';

const messageApp = new Vue({
    el: '#messageApp',
    delimiters: ['[[', ']]'],
    components:{
        'message-row': message_row,
        'message-read': message_read,
        'pagination-nav': pagination_nav,
        'form-input-group': form_input_group,
        'form-textbox-group': form_textbook_group,
        'folder-nav': folder_nav,
        'vue-boostrap-typeahead': VueBootstrapTypeahead,
        // 'form-input-typeahead': () => import('../../components/form-input-typeahead.js'),
    },
    data: {
        active_index: null,
        messages: list,//defined in script tag
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
        pagination_urls: pagination_urls,//from script tag
        selectedMessages: [],
        show: {
            newMessage: false,
        },
        urls: links,//from script tag
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
    },
    template: `
    <div>
        <folder-nav v-bind:urls="urls"
            v-bind:message-is-visible="messageIsVisible"
            v-bind:folder-is-visible="folderIsVisible"
            v-bind:new-message-is-visible="newMessageIsVisible"
            v-bind:move-links-visible="moveLinksVisible"
            v-bind:event-signal="eventSignal"
            v-on:update-active-message="updateActiveMessage($event)"
            v-on:new-message="showNewMessage"
            v-on:back-to-last="showLastPage"
            v-on:reply-to-message="replyToMessage"
            v-on:move-message="moveMessage($event)">
        </folder-nav>

        <div v-if="folderIsVisible" class="container-fluid p-1" id="folder">
            <div class="row">
                <table class="table table-hover d-flex flex-column">
                    <thead>
                        <tr class="d-flex folder-header">
                            <th class="d-none d-md-block col-1" scope="col"><input id="select_all" type="checkbox"></th>
                            <th class="" hidden scope = "col"></th>
                            <th class="col-2" scope="col">From</th>
                            <th class="col-2" scope="col">Subject</th>
                            <th class="col-6" scope="col">Body</th>
                            <th class="col-1" scope="col">Time Sent</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr is="message-row"
                            v-for="message in messages"
                            v-bind:message="message"
                            v-bind:key="message.id"
                            v-on:show-message="showMessage(message)"
                            v-on:selected-messages="updateSelectedMessages">
                        </tr>
                    </tbody>
                </table>    
                <button v-on:click="reverseMessages">Reverse Messages</button>
            </div>
            <br>
            <pagination-nav
            v-bind:pagination_urls="pagination_urls"
            v-bind:pages="pagination_urls.pages"/>
        </div>

        <div v-if="messageIsVisible">
            <message-read v-bind:message="active_message"></message-read>
        </div>

        <div v-if="newMessageIsVisible">
            <form
            method="POST"
            v-bind:action="urls.send_message"
            id="message-form">
                <input v-bind="{name: 'csrf_token', value: csrf, type:'hidden'}">
                <input v-model="newMessage.conversation_id" v-bind="{name: 'conversation_id', type:'hidden'}">
                <input v-model="newMessage.recipient_id" v-bind="{name: 'recipient_id', type:'hidden'}">
                <!-- <form-input-typeahead
                    v-if="!is_active"
                    v-model="newMessage.recipient"
                    v-bind="{name: 'recipient'}"
                    v-bind:url="urls.autocomplete"
                    v-on:id-change="newMessage.recipient_id=$event">To
                </form-input-typeahead> -->
                <form-input-group
                    v-if="is_active"
                    v-model="newMessage.recipient"
                    v-bind="{name: 'recipient', readonly: true}">To
                </form-input-group>            
                <form-input-group v-model="newMessage.subject" v-bind="{name: 'subject'}">Subject</form-input-group>
                <form-textbox-group v-model="newMessage.body" v-bind="{name: 'body'}">Message Body</form-textbox-group>
                <button
                    class="btn btn-primary btn-block submit"
                    type="submit"
                    v-on:click.prevent="sendMessage"
                    >
                    Submit
                </button>
            </form>

        </div>
    </div>    
    `
});

export default messageApp;

