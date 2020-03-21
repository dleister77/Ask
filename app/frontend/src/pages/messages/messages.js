import axios from 'axios';
import Vue from 'vue';

import {postForm, makeForm} from '../../scripts/forms.js';

import message_form from '../../components/messages/message-form';
import message_row from '../../components/messages/message-row';
import message_read from '../../components/messages/message-read';
import pagination_nav from '../../components/pagination-nav';
import folder_nav from '../../components/folder-nav';


const messageApp = new Vue({
    el: '#messageApp',
    delimiters: ['[[', ']]'],
    components:{
        'message-row': message_row,
        'message-read': message_read,
        'pagination-nav': pagination_nav,
        'message-form': message_form,
        'folder-nav': folder_nav,
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
        is_reply: false,
        newMessage: {
            message_user_id: "",
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
            let form = makeForm(data)
            axios.post(this.urls.updateMessageRead, form)
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
                'tag': status,
                'csrf_token': this.csrf
            };
            postForm(this.urls.move, form_data);
        },
        replyToMessage: function(){
            this.show.newMessage = true;
            this.is_reply = true;
        },
        reverseMessages: function(){
            this.messages.reverse();
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
                this.is_reply = false;
            } else {
                this.active_index = null;
                this.show.newMessage = false;
                this.is_reply = false;
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

        <message-form
            id="message-form"
            v-if="newMessageIsVisible"
            v-bind:urls="urls"
            v-bind:csrf="csrf"
            v-bind:is_active="is_active"
            v-bind:active_message="active_message"
            v-bind:is_reply="is_reply"
            v-on:message_sent="show.newMessage=false"/>
    </div>    
    `
});

export default messageApp;

