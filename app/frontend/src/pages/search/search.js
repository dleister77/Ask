import Vue from 'vue';
import typeahead_mixin from '../../components/typeahead_mixin';
import makeMap from '../../scripts/maps.js';
import {categoryGet} from '../../scripts/forms.js'
import { getCurrentLocation } from '../../scripts/geo.js';

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
            location: "home",
            manual_location: "",
            gpsLat: "",
            gpsLong: "",
            searchRange: 30,
            sector: 1,
            category:"",
            name: "",
        },
        map: {
            show: false,
            center: mapCenter,
            container: "mapContainer",
            isRendered: false,
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
            this.map.isRendered = true,
            makeMap(this.map, this.searchResults);
        },
        updateCategory: function(){
            categoryGet(this.urls.categoryList, this.form.sector, 'category');
        },
        makeQueryString: function(){
            let qs = Object.entries(this.filter).map(function([key,value]){
                        return `${key}=${encodeURIComponent(value)}`});
            return `?${qs.join('&')}`;
        },
        makeQueryUrl: function(){
            return this.urls.autocomplete + this.makeQueryString();
        },
    },
    mixins: [typeahead_mixin],
    mounted: function(){
        const select = document.getElementById("category");
        this.form.category = select.firstElementChild.value;
    },
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