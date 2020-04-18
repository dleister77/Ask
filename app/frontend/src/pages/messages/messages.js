import axios from 'axios';
import Vue from 'vue';
import VueSweetalert2 from 'vue-sweetalert2';
import 'sweetalert2/dist/sweetalert2.min.css';

import { postForm, makeForm } from '../../scripts/forms';

import MessageForm from '../../components/messages/message-form';
import MessageRow from '../../components/messages/message-row';
import MessageRead from '../../components/messages/message-read';
import paginationNav from '../../components/pagination-nav';
import folderNav from '../../components/folder-nav';


Vue.use(VueSweetalert2);


const messageApp = new Vue({
  el: '#messageApp',
  delimiters: ['[[', ']]'],
  components: {
    'message-row': MessageRow,
    'message-read': MessageRead,
    'pagination-nav': paginationNav,
    'message-form': MessageForm,
    'folder-nav': folderNav,
  },
  data: {
    active_index: null,
    messages: list, // defined in script tag
    csrf,
    eventSignal: {
      updateActive: 'update-active-message',
      newMessage: 'new-message',
      backToLast: 'back-to-last',
      replyToMessage: 'reply-to-message',
      moveMessage: 'move-message',
    },
    is_reply: false,
    newMessage: {
      message_user_id: '',
      recipient_id: '',
      recipient: '',
      subject: '',
      body: '',
    },
    pagination_urls, // from script tag
    selectedMessages: [],
    show: {
      newMessage: false,
    },
    urls: links, // from script tag
  },
  computed: {
    active_message() {
      if (this.active_index >= 0 && this.active_index < this.messages.length) {
        return this.messages[this.active_index];
      }
      return null;
    },
    folderIsVisible() {
      return !this.is_active && !this.newMessageIsVisible;
    },
    is_active() {
      return this.active_index != null;
    },
    messageIsVisible() {
      return this.is_active && !this.newMessageIsVisible;
    },
    moveLinksVisible() {
      return this.selectedMessages.length > 0 && !this.newMessageIsVisible;
    },
    newMessageIsVisible() {
      return this.show.newMessage;
    },
  },
  methods: {
    markAsRead() {
      const data = { id: this.active_message.id, csrf_token: this.csrf };
      const form = makeForm(data);
      axios.post(this.urls.updateMessageRead, form)
        .then((response) => {
          if (response.data.status === 'success') {
            this.active_message.read = true;
          } else {
            console.log('Error: mark as read failed.');
          }
        })
        .catch((error) => {
          console.log(error);
        });
    },
    moveMessage(status) {
      const formData = {
        message_id: this.selectedMessages.toString(),
        tag: status,
        csrf_token: this.csrf,
      };
      postForm(this.urls.move, formData);
    },
    replyToMessage() {
      this.show.newMessage = true;
      this.is_reply = true;
    },
    reverseMessages() {
      this.messages.reverse();
    },
    showMessage(message) {
      this.active_index = this.messages.indexOf(message);
      this.selectedMessages.push(message.id);
      if (!message.read) {
        this.markAsRead();
      }
    },
    showNewMessage() {
      this.show.newMessage = true;
      this.active_index = null;
    },
    showLastPage() {
      if (this.messageIsVisible) {
        this.active_index = null;
        this.selectedMessages = [];
      } else if (this.newMessageIsVisible && this.active_index != null) {
        this.show.newMessage = false;
        this.is_reply = false;
      } else {
        this.active_index = null;
        this.show.newMessage = false;
        this.is_reply = false;
      }
    },
    updateActiveMessage(adjust) {
      if (0 <= (this.active_index + adjust) < this.messages.length) {
        this.active_index += adjust;
      }
    },
    updateSelectedMessages(update) {
      const [addToSelected, id] = update;
      if (addToSelected) {
        this.selectedMessages.push(id);
      } else {
        this.selectedMessages = this.selectedMessages.filter((value) => value !== id);
      }
    },
    updateRecipientID(value) {
      this.newMessage.recipient_id = value;
    },
  },
  mounted() {
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
              <table class="table table-hover d-flex flex-column border-bottom">
                  <thead>
                      <tr class="d-flex folder-header">
                          <th class="d-none d-md-block col-1" scope="col"><input id="select_all" type="checkbox"></th>
                          <th class="" hidden scope = "col"></th>
                          <th class="col-2" scope="col">From</th>
                          <th class="col-2" scope="col">Subject</th>
                          <th class="col-6" scope="col">Body</th>
                          <th class="col-2 col-md-1" scope="col">Time Sent</th>
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

