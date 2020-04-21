import Vue from 'vue';
import { BootstrapVue } from 'bootstrap-vue';
import { VBTooltip } from 'bootstrap-vue';
import DeviceDetectionMixin from '../../components/mixins/deviceDetection';

import ModalFormUsermessageMixin from '../../components/modal-message-user-mixin';
import ModalFormSuggestionMixin from '../../components/modal-form-suggestion-mixin';
import 'bootstrap-vue/dist/bootstrap-vue.css';

Vue.use(BootstrapVue);

const profile = new Vue({
  el: '#appContent',
  directives: {
    'b-tooltip': VBTooltip,
  },
  mixins: [DeviceDetectionMixin, ModalFormUsermessageMixin, ModalFormSuggestionMixin],
  methods: {
    setActiveBusiness(id) {
      this.activeBusiness = providerJson;
    },
  },
});

export default profile;
