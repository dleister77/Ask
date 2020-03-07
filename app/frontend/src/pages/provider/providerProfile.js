import Vue from 'vue';
import modal_message_mixin from '../../components/modal-message-mixin';


const profile = new Vue({
    el: '#appContent',
    mixins: [modal_message_mixin],
});

export default profile;