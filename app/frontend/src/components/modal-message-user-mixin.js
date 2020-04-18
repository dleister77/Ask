import ModalFormWrapper from './modals/modal-form-wrapper';
import FormUsermessage from './form-usermessage';

const ModalFormUsermessageMixin = {
  components: {
    'modal-form-wrapper': ModalFormWrapper,
    'form-usermessage': FormUsermessage,
  },
  delimiters: ['[[', ']]'],
  data: {
    form_presets: {
      user_message: {
        csrf_token: csrf,
        recipient_id: '',
        recipient_name: '',
        subject: '',
      },
    },
    urls: {
      send_user_message: '/message/send',
    },
  },
  methods: {
    setFormPresets(event) {
      const source = event.target;
      this.form_presets.user_message.recipient_id = source.dataset.id;
      this.form_presets.user_message.recipient_name = source.dataset.name;
      this.form_presets.user_message.subject = source.dataset.subject;
    },
  },
};
export default ModalFormUsermessageMixin;
