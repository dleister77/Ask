import Vue from 'vue';
import ModalFormUsermessageMixin from '../../components/modal-message-user-mixin';


const user = new Vue({
  el: '#appContent',
  mixins: [ModalFormUsermessageMixin],
  mounted() {
    $('[data-toggle="tooltip"]').tooltip();
  },
});

export default user;
