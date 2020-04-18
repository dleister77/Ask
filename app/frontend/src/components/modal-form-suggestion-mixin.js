import ModalFormWrapper from './modals/modal-form-wrapper';
import FormSuggestion from './form-suggestion';


const ModalFormSuggestionMixin = {
  components: {
    'modal-form-wrapper': ModalFormWrapper,
    'form-suggestion': FormSuggestion,
  },
  delimiters: ['[[', ']]'],
  data: {
    activeBusiness: '',
    form_presets: {
      provider_suggestion: {
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
    },
    urls: {
      send_provider_suggestion: '/provider/suggestion',
    },
  },
  methods: {
    setSuggestionFormPresets(event) {
      const source = event.target;
      this.form_presets.provider_suggestion.id = source.dataset.id;
      this.form_presets.provider_suggestion.name = source.dataset.subject;
      this.setActiveBusiness(this.form_presets.provider_suggestion.id);
      this.form_presets.provider_suggestion.category = String(this.activeBusiness.category_ids).split(',').map(Number);
      this.form_presets.provider_suggestion.sector = Number(this.activeBusiness.sector_ids);
      this.form_presets.provider_suggestion.address = {
        line1: this.activeBusiness.line1,
        line2: this.activeBusiness.line2,
        city: this.activeBusiness.city,
        state: Number(this.activeBusiness.state_id),
        zip: this.activeBusiness.zip,
      };
      this.form_presets.provider_suggestion.email = this.activeBusiness.email;
      this.form_presets.provider_suggestion.website = this.activeBusiness.website;
      this.form_presets.provider_suggestion.telephone = this.activeBusiness.telephone;
    },
    setActiveBusiness(id) {
      // to be implemented by individual page
    },
  },
};
export default ModalFormSuggestionMixin;
