import Vue from 'vue';
import modal_form_usermessage_mixin from '../../components/modal-message-user-mixin';

const profile = new Vue({
    el: '#appContent',
    mixins: [modal_form_usermessage_mixin],
});

export default profile;