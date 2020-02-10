// import {Map} from 'esri';
// import {MapView} from 'esri/views';
// import {FeatureLayer} from 'esri/layers';
// import {Graphic} from 'esri'
var mapboxgl = require('mapbox-gl/dist/mapbox-gl.js');

let map;

function makeGeoJSON(businessList){
    let geojson = {
        type: 'FeatureCollection',
        features: []
    }
    businessList.forEach(element => {
        geojson.features.push({
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: [element.longitude, element.latitude],
            },
            properties: {
                name: element.name,
                telephone: element.telephone,
                line1: element.line1,
                line2: element.line2,

            }
        })
    });
    return geojson;
}

 
function makeMap(mapArgs, businessList){
    mapboxgl.accessToken = 'pk.eyJ1IjoibGVpc3RlcmJyYXUiLCJhIjoiY2s2Yzg1MTI2MTljcjNvcWJ5bTdrb2ozayJ9.qZRovROoQTGWjWl1cQqWPQ';
    
    var home = [mapArgs.center.longitude, mapArgs.center.latitude]
    
    map = new mapboxgl.Map({
        center: home,
        container: mapArgs.container,
        style: 'mapbox://styles/mapbox/streets-v11',
        zoom: 9
    });

    var homeMarker = new mapboxgl.Marker().setLngLat(home).addTo(map);
    addMarkers(businessList);
}

function addMarkers(businessList){
    // let geojson = makeGeoJSON(featureList);
    businessList.forEach(function(business){
        let marker = new mapboxgl.Marker({
            color: 'red',
        });
        marker.setLngLat([business.longitude, business.latitude])
        marker.setPopup(makeBusinessPopup(business))
        marker.addTo(map);
    })
}

function makeBusinessPopup(business){
    let popup = new mapboxgl.Popup({ offset: 25 }) // add popups
    let link = new URL(`/provider/${business.name}/${business.id}`, origin);
    popup.setHTML(`
                    <ul class="list-group list-group-flush text-left border-0">
                        <li class="map-popup-row list-group-item py-1"><a href=${link.href}>${business.name}</a></li>
                        <li class="map-popup-row list-group-item py-1">${business.categories}</li>
                        <li class="map-popup-row list-group-item py-1">${business.line1}\n
                                                    ${business.line2}\n
                                                    ${business.city}, ${business.state_short} ${business.zip}
                        </li>
                        <li class="map-popup-row list-group-item py-1">(${business.telephone.slice(0,3)}) ${business.telephone.slice(3,6)}-${business.telephone.slice(6,)}</li>
                    </ul>
                `)
    return popup;
}

export default makeMap

// function viewMap(mapContainer, mapCenter, searchResults){
//     require(["esri/Map",
//              "esri/views/MapView",
//              "esri/layers/FeatureLayer",
//              "esri/Graphic"],
//               function(Map, MapView, FeatureLayer, Graphic) {
//                 var map = new Map({
//                     basemap: "streets-navigation-vector"
//                 });
  
//                 var view = new MapView({
//                     container: mapContainer,
//                     map: map,
//                     center: [mapCenter.longitude, mapCenter.latitude], // longitude, latitude
//                     zoom: 10
//                 });

//                 var homeMarker = [new Graphic({
//                     attributes: {
//                         ObjectID: 1,
//                         address: mapCenter.address
//                     },
//                     geometry: {
//                         type: "point",
//                         longitude: mapCenter.longitude,
//                         latitude: mapCenter.latitude
//                     }
//                 })];
//                 var featureLayer = new FeatureLayer({
//                     source: homeMarker,
//                     renderer: {
//                         type: "simple",                    // autocasts as new SimpleRenderer()
//                         symbol: {                          // autocasts as new SimpleMarkerSymbol()
//                             type: "simple-marker",
//                             color: [56, 168, 0, 1],
//                             outline: {                       // autocasts as new SimpleLineSymbol()
//                                 style: "none",
//                                 color: [255, 255, 255, 0],
//                             },
//                             size: 8
//                         }
//                     },
//                     objectIdField: "ObjectID",           // This must be defined when creating a layer from `Graphic` objects
//                     fields: [
//                         {
//                             name: "ObjectID",
//                             alias: "ObjectID",
//                             type: "oid"
//                         },
//                         {
//                             name: "address",
//                             alias: "address",
//                             type: "string"
//                         }
//                     ]
//                 });
//                 map.layers.add(featureLayer);
//                 createBusinessLayer(searchResults,map);
//     });
// }

// //create graphics and add to feature layer
// function createBusinessLayer(searchResults, map){
//     require(["esri/layers/FeatureLayer","esri/Graphic"],
//             function(FeatureLayer, Graphic){
//             let origin = window.location.origin;
//             var markers = searchResults.map(function(biz){
//                 let link = new URL(`/provider/${biz.name}/${biz.id}`, origin);
//                 return new Graphic({
//                     attributes: {
//                         ObjectID: biz.id,
//                         nameLink: `<a href=${link.href}>${biz.name}</a>`,
//                         name : biz.name,
//                         categories: biz.categories.replace(",", ", "),
//                         telephone: `(${biz.telephone.slice(0,3)}) ${biz.telephone.slice(3,6)}-${biz.telephone.slice(6,)}`,
//                         email: biz.email,
//                         address: `${biz.line1} \n ${biz.city}, ${biz.state_short}`, 
//                         rating: `${(biz.reviewAverage==null) ? 'N/A' : biz.reviewAverage}`,
//                         cost: `${(biz.reviewCost==null) ? 'N/A' : biz.reviewCost}`,
//                         count: biz.reviewCount
//                     },
//                     geometry: {
//                         type: "point",
//                         longitude: biz.longitude,
//                         latitude: biz.latitude
//                     }
//                 });
//             });

//             var businessPopUp = {
//                 "title": "Business Profile",
//                 "content": [{
//                     "title": "{name}",
//                     "type": "fields",
//                     "fieldInfos": [
//                         {
//                             "fieldName": "nameLink",
//                             "label": "Name",
//                         },
//                         {
//                             "fieldName": "categories",
//                             "label": "Categories",
//                         },
//                         {
//                             "fieldName": "address",
//                             "label": "Address",
//                         },
//                         {
//                             "fieldName": "telephone",
//                             "label": "Telephone",
//                         },
//                         {
//                             "fieldName": "rating",
//                             "label": "Avg. Rating",
//                         },
//                         {
//                             "fieldName": "cost",
//                             "label": "Avg. cost",
//                         },
//                         {
//                             "fieldName": "count",
//                             "label": "# Reviews",
//                         },                                                 
//                     ]
//                 }]
//             };

//             var businessLabels = {
//                 // autocasts as new LabelClass()
//                 symbol: {
//                     type: "text",
//                     color: [0,0,0,255],  // black
//                     font: { family: "sans-serif", size: 10, weight: "normal" }
//                 },
//                 labelPlacement: "center-right",
//                 labelExpressionInfo: {
//                   expression: "$feature.name"
//                 }
//             };

//             var featureLayer = new FeatureLayer({
//                 source: markers,
//                 renderer: {
//                     type: "simple", // autocasts as new SimpleRenderer()
//                     symbol: {// autocasts as new SimpleMarkerSymbol()
//                         type: "simple-marker",
//                         color: [255,0,0],
//                         outline: { // autocasts as new SimpleLineSymbol()
//                             style: "none",
//                             color: [255, 255, 255, 0]
//                         },
//                         size: 8
//                     }
//                 },
//                 objectIdField: "ObjectID", // This must be defined when creating a layer from `Graphic` objects
//                 fields: [
//                     {
//                         name: "ObjectID",
//                         alias: "ObjectID",
//                         type: "oid"
//                     },
//                     {
//                         name: "address",
//                         alias: "address",
//                         type: "string"
//                     },
//                     {
//                         name: "nameLink",
//                         alias: "nameLink",
//                         type: "string"
//                     },                    
//                     {
//                         name: "name",
//                         alias: "name",
//                         type: "string"
//                     },
//                     {
//                         name: "categories",
//                         alias: "categories",
//                         type: "string"
//                     },
//                     {
//                         name: "telephone",
//                         alias: "telephone",
//                         type: "string"
//                     },
//                     {
//                         name: "rating",
//                         alias: "rating",
//                         type: "string"
//                     },
//                     {
//                         name: "cost",
//                         alias: "cost",
//                         type: "string"               
//                     },
//                     {
//                         name: "count",
//                         alias: "count",
//                         type: "integer"               
//                     }
//                 ],
//                 popupTemplate: businessPopUp,
//                 labelingInfo: [businessLabels]
//             });
//             map.layers.add(featureLayer)
//     });
// }
// export default viewMap;