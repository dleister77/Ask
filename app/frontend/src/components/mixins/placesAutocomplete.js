import { states } from '../../../supporting/states';

const places = require('places.js');


const placesAutocomplete = {
  data() {
    return {
      form: {
        line1: '',
        city: '',
        zip: '',
        state: '',
      },
      placesAutocomplete: null,
      states,
      placesOptions: {
        appId: 'pl3FNF3N3O3N',
        apiKey: '585cacc884f34cf6ed0bf7c6d0143f8c',
        container: '#address-line1',
        type: 'address',
        countries: ['us'],
        useDeviceLocation: true,
        aroundLatLngViaIP: true,
        templates: {
          value(s) {
            return s.name;
          },
          suggestion(s) {
            return `${s.highlight.name}, ${s.highlight.city}, ${s.highlight.administrative}`;
          },
        },
      },
    };
  },
  methods: {
    init_places() {
      this.placesAutocomplete = places(this.placesOptions);

      this.placesAutocomplete.on('change', (e) => {
        this.form.address.state = this.get_state(e.suggestion.administrative) || 1;
        this.form.address.city = e.suggestion.city || '';
        this.form.address.zip = e.suggestion.postcode || '';
      });
    },
    get_state(state) {
      const s = this.states.find((item) => item.name === state);
      return s.id;
    },
  },
  mounted() {
    this.init_places();

  },
};

export default placesAutocomplete;
