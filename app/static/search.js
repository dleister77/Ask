import {categoryGet} from './scripts/forms.js';
import {ready} from './scripts/helpers.js';
import {request_location} from './scripts/geo.js'


ready(function(){
    document.getElementById('sector').addEventListener("change", function(){
        let url = '/categorylist'
        categoryGet(url, 'sector', 'category');
    });

    let locationSource = document.getElementById("location");
    let lat = document.getElementById("gpsLat");
    let long = document.getElementById("gpsLong");
    locationSource.addEventListener('input', function(){
        if (locationSource.value == 'gps') {
            request_location(lat, long);
        } 
    })


});