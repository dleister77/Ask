import Vue from 'vue';
import modal_message_user_mixin from '../../components/modal-message-user-mixin';


const user = new Vue({
    el: '#appContent',
    mixins: [modal_message_user_mixin],
});

export default user;