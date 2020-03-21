import form_input from '../forms/form-input';
import form_textbox from '../forms/form-textbox';

import axios from 'axios';
import _ from 'lodash';
import typeahead_mixin from '../forms/typeahead_mixin';


let message_form = {
    components: {
        'form-input': form_input,
        'form-textbox': form_textbox,
    },
    mixins: [typeahead_mixin],
    data: function(){
        return {
            form: {
                message_user_id: "",
                recipient_id: "",
                recipient: "",
                subject: "",
                body: "",
            },
            typeahead: {
                name_field: 'recipient',
                id_field: 'recipient_id'
            }
        }
    },
    props:{
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
    methods:{
        replyToMessage: function(){
            this.form.message_user_id = this.active_message.id;
            this.form.recipient_id = this.active_message.sender_id;
            this.form.recipient = this.active_message.sender_full_name;
            if (this.active_message.subject.startsWith("Re:")){
                this.form.subject = this.active_message.subject;
            } else {
                this.form.subject = `Re: ${this.active_message.subject}`;
            }
            this.form.body = `\n\nOn ${this.active_message.timestamp}, ${this.active_message.sender_full_name} wrote:\n${this.active_message.body}`
        },
        sendMessage: function(){
            let self = this;
            const f = new FormData(document.getElementById('message-form'));
            axios.post(this.urls.send_message, f)
            .then(function(response){
                if (response.data.status == 'success'){
                    self.$emit('message_sent');
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
        suggestionSerializer: function(person){
            return person.full_name;
        }

    },
    mounted: function(){
        if (this.is_reply == true){
            this.replyToMessage();
        }
    },
    watch:{
        'form.recipient': function(val){
            const debouncedGetSuggestions = _.debounce(this.getSuggestions, 500);
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
        
        <input v-model="form.recipient" name='recipient' type='hidden'>
        
        <div class="form-group">
            <label
            for="recipient_typeahead"
            v-if="!is_active">To</label>
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
            :name='recipient'
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
            class="btn btn-primary btn-block submit"
            type="submit"
            v-on:click.prevent="sendMessage"
            >
            Submit
        </button>
    </form>
    `,
}

export default message_form;