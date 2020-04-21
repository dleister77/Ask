import Vue from 'vue';
import { BootstrapVue } from 'bootstrap-vue';
import { VBTooltip } from 'bootstrap-vue';
import TypeaheadMixin from '../../components/forms/typeahead_mixin';
import makeMap from '../../scripts/maps';
import { categoryGet } from '../../scripts/forms';
import { getCurrentLocation } from '../../scripts/geo';
import ModalFormSuggestionMixin from '../../components/modal-form-suggestion-mixin';
import DeviceDetectionMixin from '../../components/mixins/deviceDetection';
// import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap-vue/dist/bootstrap-vue.css';


Vue.use(BootstrapVue);

const mapView = {
  template: '<div></div>',
};

const searchPage = new Vue({
  el: '#appContent',
  delimiters: ['[[', ']]'],
  directives: {
    'b-tooltip': VBTooltip,
  },
  components: {
    'map-view': mapView,
  },
  computed: {
    showManualLocation() {
      return this.form.location === 'manual';
    },
    filter() {
      return {
        sector: this.form.sector,
        category: this.form.category,
        location: this.form.location,
        manual_location: this.form.manual_location,
        searchRange: this.form.searchRange,
        name: this.form.name,
      };
    },
  },
  data: {
    activeView: 'list',
    form: {
      location: form_json.location,
      manual_location: form_json.manual_location,
      gpsLat: form_json.gpsLat,
      gpsLong: form_json.gpsLong,
      searchRange: form_json.searchRange,
      sector: form_json.sector,
      category: form_json.category,
      name: form_json.name,
    },
    map: {
      show: false,
      center: mapCenter,
      container: 'mapContainer',
    },
    searchResults,
    typeahead: {
      include_id: false,
    },
    views: ['list', 'map'],
    urls: links,
  },
  methods: {
    renderMap() {
      this.map.show = true;
      Vue.nextTick(() => makeMap(this.map, this.searchResults));
    },
    updateCategory() {
      categoryGet(this.urls.categoryList, this.form.sector, 'search_category');
    },
    makeQueryString() {
      const qs = Object.entries(this.filter).map(([key, value]) => {
        return `${key}=${encodeURIComponent(value)}`;
      });
      return `?${qs.join('&')}`;
    },
    makeQueryUrl() {
      return this.urls.autocomplete + this.makeQueryString();
    },
    setActiveBusiness(id) {
      const b = this.searchResults.filter((business) => business.id === Number(id))[0];
      this.activeBusiness = b;
    },
  },
  mixins: [DeviceDetectionMixin, TypeaheadMixin, ModalFormSuggestionMixin],
  watch: {
    'form.location': function (locationSource) {
      if (locationSource === "gps") {
        getCurrentLocation()
          .then((position) => {
            this.form.gpsLat = position.latitude;
            this.form.gpsLong = position.longitude;
          })
          .catch((error) => {
            console.log(`Error: ${error.message}`);
          });
      } else {
        this.form.gpsLat = '';
        this.form.gpsLong = '';
      }
    },
  },
});

export default searchPage;
