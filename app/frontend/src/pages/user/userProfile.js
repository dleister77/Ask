import Vue from 'vue';
import { BootstrapVue } from 'bootstrap-vue';
import { VBTooltip } from 'bootstrap-vue';
import ModalFormUsermessageMixin from '../../components/modal-message-user-mixin';
import DeviceDetectionMixin from '../../components/mixins/deviceDetection';

import 'bootstrap-vue/dist/bootstrap-vue.css';

Vue.use(BootstrapVue);

const user = new Vue({
  el: '#appContent',
  directives: {
    'b-tooltip': VBTooltip,
  },
  mixins: [DeviceDetectionMixin, ModalFormUsermessageMixin],
});

export default user;
