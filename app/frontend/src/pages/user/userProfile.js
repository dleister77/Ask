import Vue from 'vue';
import modal_message_mixin from '../../components/modal-message-mixin';


const user = new Vue({
    el: '#appContent',
    mixins: [modal_message_mixin],
});

export default user;