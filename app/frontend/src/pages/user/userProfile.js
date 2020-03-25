import Vue from 'vue';
import ModalFormUsermessageMixin from '../../components/modal-message-user-mixin';


const user = new Vue({
  el: '#appContent',
  mixins: [ModalFormUsermessageMixin],
});

export default user;
