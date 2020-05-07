import Vue from 'vue';
import { VueMaskDirective } from 'v-mask';
import { categoryGet } from '../../scripts/forms';
import placesAutocomplete from '../../components/mixins/placesAutocomplete';


const providerAdd = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  directives: {
    mask: VueMaskDirective,
  },
  mixins: [placesAutocomplete],
  data: {
    form: {
      name: form_server.name,
      sector: form_server.sector != null ? form_server.sector : 1,
      category: form_server.category != null ? form_server.category : [1],
      email: form_server.email,
      website: form_server.website,
      telephone: form_server.telephone,
      address: {
        unknown: form_server.address.unknown,
        line1: form_server.address.line1,
        line2: form_server.address.line2,
        city: form_server.address.city,
        zip: form_server.address.zip,
        state: form_server.address.state,
      }
    },
    urls: links,
  },
  methods: {
    updateCategory() {
      categoryGet(this.urls.categoryList, this.form.sector, 'category');
      this.form.category = [];
    },
  },
});

export default providerAdd;
