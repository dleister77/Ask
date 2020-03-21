import Vue from 'vue';
import typeahead_mixin from '../../components/forms/typeahead_mixin';
import makeMap from '../../scripts/maps.js';
import {categoryGet} from '../../scripts/forms.js'
import { getCurrentLocation } from '../../scripts/geo.js';
import modal_form_correction_mixin from '../../components/modal-form-correction-mixin';
import form_suggestion from '../../components/form-suggestion';

var mapboxgl = require('mapbox-gl/dist/mapbox-gl.js');

const mapView = {
    template: `<div></div>`
}

const searchPage = new Vue({
    el: '#appContent',
    delimiters: ['[[', ']]'],
    components:{
        'map-view': mapView,
        'vue-bootstrap-typeahead': VueBootstrapTypeahead,
        'form-suggestion': form_suggestion,
    },
    computed:{
        showManualLocation: function(){
            return this.form.location == 'manual';
        },
        filter: function(){
            return {
                sector: this.form.sector,
                category: this.form.category,
                location: this.form.location,
                manual_location: this.form.manual_location,
                searchRange: this.form.searchRange,
                name: this.form.name,
            }
        }
    },
    data: {
        activeView: 'list',
        form:{
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
            container: "mapContainer",
        },
        searchResults: searchResults,
        typeahead: {
            include_id: false,
        },
        views: ['list', 'map'],
        urls: links,
    },
    methods: {
        renderMap: function(){
            this.map.show = true;
            let self = this;
            Vue.nextTick(function() {
                    makeMap(self.map, self.searchResults);
                });
        },
        updateCategory: function(){
            categoryGet(this.urls.categoryList, this.form.sector, 'search_category');
        },
        makeQueryString: function(){
            let qs = Object.entries(this.filter).map(function([key,value]){
                        return `${key}=${encodeURIComponent(value)}`});
            return `?${qs.join('&')}`;
        },
        makeQueryUrl: function(){
            return this.urls.autocomplete + this.makeQueryString();
        },
        setActiveBusiness: function(id) {
            let b = this.searchResults.filter((business)=> business.id == id)[0]
            this.activeBusiness = b;
        }
    },
    mixins: [typeahead_mixin, modal_form_correction_mixin],
    watch: {
        'form.location': function(locationSource){
            if (locationSource == "gps"){
                getCurrentLocation()
                .then((position) => {
                    this.form.gpsLat = position.latitude;
                    this.form.gpsLong = position.longitude;
                })
                .catch((error) => {
                    console.log(`Error: ${error.message}`)
                })
            } else {
                this.form.gpsLat = "";
                this.form.gpsLong = "";
            }
        },
    }
});

export default searchPage;