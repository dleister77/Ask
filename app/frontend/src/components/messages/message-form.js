/* eslint-disable func-names */
import axios from 'axios';
import debounce from 'lodash-es/debounce';

import FormInput from '../forms/form-input';
import FormTextbox from '../forms/form-textbox';
import TypeaheadMixin from '../forms/typeahead_mixin';


const MessageForm = {
  components: {
    'form-input': FormInput,
    'form-textbox': FormTextbox,
  },
  mixins: [TypeaheadMixin],
  data() {
    return {
      form: {
        message_user_id: '',
        recipient_id: '',
        recipient: '',
        subject: '',
        body: '',
      },
      typeahead: {
        name_field: 'recipient',
        id_field: 'recipient_id',
      },
    };
  },
  props: {
    active_message: {
      type: Object,
      required: false,
    },
    csrf: {
      type: String,
      required: true,
    },
    is_active: {
      type: Boolean,
      required: false,
    },
    is_reply: {
      type: Boolean,
      required: false,
    },
  },
  methods: {
    replyToMessage() {
      this.form.message_user_id = this.active_message.id;
      this.form.recipient_id = this.active_message.sender_id;
      this.form.recipient = this.active_message.sender_full_name;
      if (this.active_message.subject.startsWith('Re:')) {
        this.form.subject = this.active_message.subject;
      } else {
        this.form.subject = `Re: ${this.active_message.subject}`;
      }
      this.form.body = `\n\nOn ${this.active_message.timestamp}, ${this.active_message.sender_full_name} wrote:\n${this.active_message.body}`;
    },
    sendMessage() {
      const f = new FormData(document.getElementById('message-form'));
      axios.post(this.urls.send_message, f)
        .then((response) => {
          if (response.data.status === 'success') {
            this.$emit('message_sent');
            this.$swal({
              title: 'Message Sent',
              icon: 'success',
            });
          } else {
            let message = 'Unabled to send message. Please correct errors:\n';
            message += response.data.errorMsg.join('\n');
            this.$swal(message);
          }
        })
        .catch((error) => {
          console.log(error);
          this.$swal({
            title: 'Error',
            text: 'Unable to send message.  Please reload and try again.',
            icon: 'error',
          });
        });
    },
    suggestionSerializer(person) {
      return person.full_name;
    },

  },
  mounted() {
    if (this.is_reply === true) {
      this.replyToMessage();
    }
  },
  watch: {
    'form.recipient': function() {
      const debouncedGetSuggestions = debounce(this.getSuggestions, 500);
      debouncedGetSuggestions();
    },
  },
  template: `
  <form
  method="POST"
  v-bind:action="urls.send_message"
  id="message-form">
      <input v-bind="{name: 'csrf_token', value: csrf, type:'hidden'}">
      
      <input v-model="form.message_user_id" v-bind="{name: 'message_user_id', type:'hidden'}">
      
      <input v-model="form.recipient_id" v-bind="{name: 'recipient_id', type:'hidden'}">
      
      
      <div class="form-group">
          <label
          for="recipient_typeahead"
          v-if="!is_active">To</label>
          <input v-model="form.recipient" name='recipient' type='hidden'> 
          <vue-bootstrap-typeahead
              id="recipient_typeahead"
              name="recipient_typeahead"
              v-if="!is_active"
              v-bind:data="typeahead.suggestions"
              v-model="form.recipient"
              v-bind:serializer="suggestionSerializer"
              placeholder="Enter name of friend..."
              @hit="typeahead.selected=$event"/>
      </div>

      <form-input
          v-if="is_active"
          v-model="form.recipient"
          name='recipient'
          :readonly=true
          :required=false>
          To
      </form-input>

      <form-input
          v-model="form.subject"
          name='subject'
          :required=false>
          Subject
      </form-input>

      <form-textbox
          v-model="form.body"
          name='body'
          :required=false>
          Message Body
      </form-textbox>

      <button
          id="message-form-submit"
          class="btn btn-primary btn-block submit"
          type="submit"
          v-on:click.prevent="sendMessage"
          >
          Submit
      </button>
  </form>
  `,
}

export default MessageForm;
