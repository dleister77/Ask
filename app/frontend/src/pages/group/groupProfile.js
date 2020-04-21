import Vue from 'vue';
import { BootstrapVue } from 'bootstrap-vue';
import { VBTooltip } from 'bootstrap-vue';

import DeviceDetectionMixin from '../../components/mixins/deviceDetection';
import ModalFormUsermessageMixin from '../../components/modal-message-user-mixin';


import 'bootstrap-vue/dist/bootstrap-vue.css';

Vue.use(BootstrapVue);

const groupProfile = new Vue({
  el: '#appContent',
  delimiters: ['[[', ']]'],
  mixins: [DeviceDetectionMixin, ModalFormUsermessageMixin],
  directives: {
    'b-tooltip': VBTooltip,
  },
});

export default groupProfile;
