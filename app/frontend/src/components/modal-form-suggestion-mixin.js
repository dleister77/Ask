import ModalFormWrapper from './modals/modal-form-wrapper';


const ModalFormSuggestionMixin = {
  components: {
    'modal-form-wrapper': ModalFormWrapper,
  },
  delimiters: ['[[', ']]'],
  data: {
    activeBusiness: '',
    form_presets: {
      csrf_token: csrf,
      id: '',
      name: '',
      address: {
        line1: '',
        line2: '',
        city: '',
        state: '',
        zip: '',
        coordinate_error: false,
      },
      sector: '',
      category: '',
      email: '',
      website: '',
      telephone: '',
    },
    urls: {
      send_message: '/provider/suggestion',
    },
  },
  methods: {
    setFormPresets(event) {
      const source = event.target;
      this.form_presets.id = source.dataset.id;
      this.form_presets.name = source.dataset.subject;
      this.setActiveBusiness(this.form_presets.id);
      this.form_presets.category = String(this.activeBusiness.category_ids).split(',').map(Number);
      this.form_presets.sector = Number(this.activeBusiness.sector_ids);
      this.form_presets.address = {
        line1: this.activeBusiness.line1,
        line2: this.activeBusiness.line2,
        city: this.activeBusiness.city,
        state: Number(this.activeBusiness.state_id),
        zip: this.activeBusiness.zip,
      };
      this.form_presets.email = this.activeBusiness.email;
      this.form_presets.website = this.activeBusiness.website;
      this.form_presets.telephone = this.activeBusiness.telephone;
    },
    setActiveBusiness(id) {
      // to be implemented by individual page
    },
  },
};
export default ModalFormSuggestionMixin;
