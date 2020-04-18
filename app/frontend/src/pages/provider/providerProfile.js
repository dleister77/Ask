import Vue from 'vue';
import ModalFormUsermessageMixin from '../../components/modal-message-user-mixin';
import ModalFormSuggestionMixin from '../../components/modal-form-suggestion-mixin';

const profile = new Vue({
  el: '#appContent',
  mixins: [ModalFormUsermessageMixin, ModalFormSuggestionMixin],
  methods: {
    setActiveBusiness(id) {
      this.activeBusiness = providerJson;
    },
  },
  mounted() {
    $('[data-toggle="tooltip"]').tooltip();
  },
});

export default profile;
