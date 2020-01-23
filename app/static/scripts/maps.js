

function viewMap(mapContainer, mapCenter, searchResults){
    require(["esri/Map",
             "esri/views/MapView",
             "esri/layers/FeatureLayer",
             "esri/Graphic"],
              function(Map, MapView, FeatureLayer, Graphic) {
                var map = new Map({
                    basemap: "streets-navigation-vector"
                });
  
                var view = new MapView({
                    container: mapContainer,
                    map: map,
                    center: [mapCenter.longitude, mapCenter.latitude], // longitude, latitude
                    zoom: 10
                });

                var homeMarker = [new Graphic({
                    attributes: {
                        ObjectID: 1,
                        address: mapCenter.address
                    },
                    geometry: {
                        type: "point",
                        longitude: mapCenter.longitude,
                        latitude: mapCenter.latitude
                    }
                })];
                var featureLayer = new FeatureLayer({
                    source: homeMarker,
                    renderer: {
                        type: "simple",                    // autocasts as new SimpleRenderer()
                        symbol: {                          // autocasts as new SimpleMarkerSymbol()
                            type: "simple-marker",
                            color: [56, 168, 0, 1],
                            outline: {                       // autocasts as new SimpleLineSymbol()
                                style: "none",
                                color: [255, 255, 255, 0],
                            },
                            size: 8
                        }
                    },
                    objectIdField: "ObjectID",           // This must be defined when creating a layer from `Graphic` objects
                    fields: [
                        {
                            name: "ObjectID",
                            alias: "ObjectID",
                            type: "oid"
                        },
                        {
                            name: "address",
                            alias: "address",
                            type: "string"
                        }
                    ]
                });
                map.layers.add(featureLayer);
                createBusinessLayer(searchResults,map);
    });
}

//create graphics and add to feature layer
function createBusinessLayer(searchResults, map){
    require(["esri/layers/FeatureLayer","esri/Graphic"],
            function(FeatureLayer, Graphic){
            let origin = window.location.origin;
            var markers = searchResults.map(function(biz){
                let link = new URL(`/provider/${biz.name}/${biz.id}`, origin);
                return new Graphic({
                    attributes: {
                        ObjectID: biz.id,
                        nameLink: `<a href=${link.href}>${biz.name}</a>`,
                        name : biz.name,
                        categories: biz.categories.replace(",", ", "),
                        telephone: `(${biz.telephone.slice(0,3)}) ${biz.telephone.slice(3,6)}-${biz.telephone.slice(6,)}`,
                        email: biz.email,
                        address: `${biz.line1} \n ${biz.city}, ${biz.state_short}`, 
                        rating: `${(biz.reviewAverage==null) ? 'N/A' : biz.reviewAverage}`,
                        cost: `${(biz.reviewCost==null) ? 'N/A' : biz.reviewCost}`,
                        count: biz.reviewCount
                    },
                    geometry: {
                        type: "point",
                        longitude: biz.longitude,
                        latitude: biz.latitude
                    }
                });
            });

            var businessPopUp = {
                "title": "Business Profile",
                "content": [{
                    "title": "{name}",
                    "type": "fields",
                    "fieldInfos": [
                        {
                            "fieldName": "nameLink",
                            "label": "Name",
                        },
                        {
                            "fieldName": "categories",
                            "label": "Categories",
                        },
                        {
                            "fieldName": "address",
                            "label": "Address",
                        },
                        {
                            "fieldName": "telephone",
                            "label": "Telephone",
                        },
                        {
                            "fieldName": "rating",
                            "label": "Avg. Rating",
                        },
                        {
                            "fieldName": "cost",
                            "label": "Avg. cost",
                        },
                        {
                            "fieldName": "count",
                            "label": "# Reviews",
                        },                                                 
                    ]
                }]
            };

            var businessLabels = {
                // autocasts as new LabelClass()
                symbol: {
                    type: "text",
                    color: [0,0,0,255],  // black
                    font: { family: "sans-serif", size: 10, weight: "normal" }
                },
                labelPlacement: "center-right",
                labelExpressionInfo: {
                  expression: "$feature.name"
                }
            };

            var featureLayer = new FeatureLayer({
                source: markers,
                renderer: {
                    type: "simple", // autocasts as new SimpleRenderer()
                    symbol: {// autocasts as new SimpleMarkerSymbol()
                        type: "simple-marker",
                        color: [255,0,0],
                        outline: { // autocasts as new SimpleLineSymbol()
                            style: "none",
                            color: [255, 255, 255, 0]
                        },
                        size: 8
                    }
                },
                objectIdField: "ObjectID", // This must be defined when creating a layer from `Graphic` objects
                fields: [
                    {
                        name: "ObjectID",
                        alias: "ObjectID",
                        type: "oid"
                    },
                    {
                        name: "address",
                        alias: "address",
                        type: "string"
                    },
                    {
                        name: "nameLink",
                        alias: "nameLink",
                        type: "string"
                    },                    
                    {
                        name: "name",
                        alias: "name",
                        type: "string"
                    },
                    {
                        name: "categories",
                        alias: "categories",
                        type: "string"
                    },
                    {
                        name: "telephone",
                        alias: "telephone",
                        type: "string"
                    },
                    {
                        name: "rating",
                        alias: "rating",
                        type: "string"
                    },
                    {
                        name: "cost",
                        alias: "cost",
                        type: "string"               
                    },
                    {
                        name: "count",
                        alias: "count",
                        type: "integer"               
                    }
                ],
                popupTemplate: businessPopUp,
                labelingInfo: [businessLabels]
            });
            map.layers.add(featureLayer)
    });
}

export default viewMap;