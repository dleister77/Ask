(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["search"],{

/***/ "6QYc":
/*!***************************************************!*\
  !*** ./src/components/form-message-correction.js ***!
  \***************************************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, exports) {

eval("throw new Error(\"Module parse failed: Unexpected keyword 'this' (134:12)\\nYou may need an appropriate loader to handle this file type, currently no loaders are configured to process this file. See https://webpack.js.org/concepts#loaders\\n|         resetForm: function() {\\n|             let self = this,\\n>             this.$v.$reset();\\n|             Object.entries(this.form).forEach(function([key, value], self) {\\n|                 if (typeof value == 'boolean'){\");\n\n//# sourceURL=webpack:///./src/components/form-message-correction.js?");

/***/ }),

/***/ "Moj8":
/*!****************************************************!*\
  !*** ./src/components/modal-message-correction.js ***!
  \****************************************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("/* harmony import */ var _modal_mixin__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./modal-mixin */ \"ejPx\");\n/* harmony import */ var _form_message_correction__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./form-message-correction */ \"6QYc\");\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! axios */ \"vDqi\");\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_2__);\n\n\n\n\n\n\nlet modal_message = {\n    components: {\n        'form-message-correction': _form_message_correction__WEBPACK_IMPORTED_MODULE_1__[/* default */ \"a\"],\n    },\n    mixins: [_modal_mixin__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"]],\n    data: function(){\n        return {\n            reset_form: false,\n            form_is_valid: false,\n        }\n    },\n    delimiters: [\"[[\", \"]]\"],\n    props: {\n        form_presets: {\n            type: Object,\n            required: false,\n        },\n        url: {\n            type: String,\n            required: true,\n        },\n    },\n    methods: {\n        resetFormPresets: function() {\n            this.reset_form = false;\n            this.$emit('reset_form_presets');\n        },\n        setValidity: function(form_is_valid_payload) {\n            this.form_is_valid = form_is_valid_payload;\n        },\n        sendMessage: function(){\n            if (!this.form_is_valid){\n                alert(\"Please correct errors and resubmit\")\n            } else {\n                let self = this;\n                const form = new FormData(document.getElementById('message-form'));\n                axios__WEBPACK_IMPORTED_MODULE_2___default.a.post(this.url, form)\n                .then(function(response){\n                    if (response.data.status == 'success'){\n                        alert(\"Message sent\");\n                        self.toggleModal()\n                    } else {\n                        let message = \"Unabled to send message. Please correct errors:\\n\"\n                        message += response.data.errorMsg.join('\\n');\n                        alert(message);\n                    }\n                })\n                .catch(function(error){\n                    console.log(error);\n                    alert(\"Error: Unable to send message.  Please reload and try again.\")\n                })\n            }\n        },\n    },\n    template: `\n    <div>\n        <modal\n            title=\"Suggest a Correction\"\n            :modal_id=\"modal_id\"\n            @modal_hide=\"reset_form=true\">\n            <template v-slot:body>\n                <form-message-correction\n                    :form_presets=\"form_presets\"\n                    :url=\"url\"\n                    :reset_form=\"reset_form\"\n                    @form_is_reset=\"resetFormPresets\"\n                    @form_is_valid=\"setValidity\">\n                </form-message-correction>\n            </template>\n            <template v-slot:footer>           \n                <button\n                    class=\"btn btn-primary btn-block submit\"\n                    type=\"submit\"\n                    v-on:click.prevent=\"sendMessage\">\n                    Submit\n                </button>\n            </template>\n        </modal>\n    </div>\n    \n    `\n}\n\n/* harmony default export */ __webpack_exports__[\"a\"] = (modal_message);\n\n//# sourceURL=webpack:///./src/components/modal-message-correction.js?");

/***/ }),

/***/ "OWs1":
/*!****************************************!*\
  !*** external "VueBootstrapTypeahead" ***!
  \****************************************/
/*! no static exports found */
/*! exports used: default */
/***/ (function(module, exports) {

eval("module.exports = VueBootstrapTypeahead;\n\n//# sourceURL=webpack:///external_%22VueBootstrapTypeahead%22?");

/***/ }),

/***/ "S2O+":
/*!*****************************!*\
  !*** ./src/scripts/maps.js ***!
  \*****************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("// import {Map} from 'esri';\n// import {MapView} from 'esri/views';\n// import {FeatureLayer} from 'esri/layers';\n// import {Graphic} from 'esri'\nvar mapboxgl = __webpack_require__(/*! mapbox-gl/dist/mapbox-gl.js */ \"4ZJM\");\n\nlet map;\n\nfunction makeGeoJSON(businessList){\n    let geojson = {\n        type: 'FeatureCollection',\n        features: []\n    }\n    businessList.forEach(element => {\n        geojson.features.push({\n            type: 'Feature',\n            geometry: {\n                type: 'Point',\n                coordinates: [element.longitude, element.latitude],\n            },\n            properties: {\n                name: element.name,\n                telephone: element.telephone,\n                line1: element.line1,\n                line2: element.line2,\n\n            }\n        })\n    });\n    return geojson;\n}\n\n \nfunction makeMap(mapArgs, businessList){\n    mapboxgl.accessToken = 'pk.eyJ1IjoibGVpc3RlcmJyYXUiLCJhIjoiY2s2Yzg1MTI2MTljcjNvcWJ5bTdrb2ozayJ9.qZRovROoQTGWjWl1cQqWPQ';\n    \n    var home = [mapArgs.center.longitude, mapArgs.center.latitude]\n    \n    map = new mapboxgl.Map({\n        center: home,\n        container: mapArgs.container,\n        style: 'mapbox://styles/mapbox/streets-v11',\n        zoom: 9\n    });\n\n    var homeMarker = new mapboxgl.Marker().setLngLat(home).addTo(map);\n    addMarkers(businessList);\n}\n\nfunction addMarkers(businessList){\n    // let geojson = makeGeoJSON(featureList);\n    businessList.forEach(function(business){\n        let marker = new mapboxgl.Marker({\n            color: 'red',\n        });\n        marker.setLngLat([business.longitude, business.latitude])\n        marker.setPopup(makeBusinessPopup(business))\n        marker.addTo(map);\n    })\n}\n\nfunction makeBusinessPopup(business){\n    let popup = new mapboxgl.Popup({ offset: 25 }) // add popups\n    let link = new URL(`/provider/${business.name}/${business.id}`, origin);\n    popup.setHTML(`\n                    <ul class=\"list-group list-group-flush text-left border-0\">\n                        <li class=\"map-popup-row list-group-item py-1\"><a href=${link.href}>${business.name}</a></li>\n                        <li class=\"map-popup-row list-group-item py-1\">${business.categories}</li>\n                        <li class=\"map-popup-row list-group-item py-1\">${business.line1}\\n\n                                                    ${business.line2}\\n\n                                                    ${business.city}, ${business.state_short} ${business.zip}\n                        </li>\n                        <li class=\"map-popup-row list-group-item py-1\">(${business.telephone.slice(0,3)}) ${business.telephone.slice(3,6)}-${business.telephone.slice(6,)}</li>\n                    </ul>\n                `)\n    return popup;\n}\n\n/* harmony default export */ __webpack_exports__[\"a\"] = (makeMap);\n\n// function viewMap(mapContainer, mapCenter, searchResults){\n//     require([\"esri/Map\",\n//              \"esri/views/MapView\",\n//              \"esri/layers/FeatureLayer\",\n//              \"esri/Graphic\"],\n//               function(Map, MapView, FeatureLayer, Graphic) {\n//                 var map = new Map({\n//                     basemap: \"streets-navigation-vector\"\n//                 });\n  \n//                 var view = new MapView({\n//                     container: mapContainer,\n//                     map: map,\n//                     center: [mapCenter.longitude, mapCenter.latitude], // longitude, latitude\n//                     zoom: 10\n//                 });\n\n//                 var homeMarker = [new Graphic({\n//                     attributes: {\n//                         ObjectID: 1,\n//                         address: mapCenter.address\n//                     },\n//                     geometry: {\n//                         type: \"point\",\n//                         longitude: mapCenter.longitude,\n//                         latitude: mapCenter.latitude\n//                     }\n//                 })];\n//                 var featureLayer = new FeatureLayer({\n//                     source: homeMarker,\n//                     renderer: {\n//                         type: \"simple\",                    // autocasts as new SimpleRenderer()\n//                         symbol: {                          // autocasts as new SimpleMarkerSymbol()\n//                             type: \"simple-marker\",\n//                             color: [56, 168, 0, 1],\n//                             outline: {                       // autocasts as new SimpleLineSymbol()\n//                                 style: \"none\",\n//                                 color: [255, 255, 255, 0],\n//                             },\n//                             size: 8\n//                         }\n//                     },\n//                     objectIdField: \"ObjectID\",           // This must be defined when creating a layer from `Graphic` objects\n//                     fields: [\n//                         {\n//                             name: \"ObjectID\",\n//                             alias: \"ObjectID\",\n//                             type: \"oid\"\n//                         },\n//                         {\n//                             name: \"address\",\n//                             alias: \"address\",\n//                             type: \"string\"\n//                         }\n//                     ]\n//                 });\n//                 map.layers.add(featureLayer);\n//                 createBusinessLayer(searchResults,map);\n//     });\n// }\n\n// //create graphics and add to feature layer\n// function createBusinessLayer(searchResults, map){\n//     require([\"esri/layers/FeatureLayer\",\"esri/Graphic\"],\n//             function(FeatureLayer, Graphic){\n//             let origin = window.location.origin;\n//             var markers = searchResults.map(function(biz){\n//                 let link = new URL(`/provider/${biz.name}/${biz.id}`, origin);\n//                 return new Graphic({\n//                     attributes: {\n//                         ObjectID: biz.id,\n//                         nameLink: `<a href=${link.href}>${biz.name}</a>`,\n//                         name : biz.name,\n//                         categories: biz.categories.replace(\",\", \", \"),\n//                         telephone: `(${biz.telephone.slice(0,3)}) ${biz.telephone.slice(3,6)}-${biz.telephone.slice(6,)}`,\n//                         email: biz.email,\n//                         address: `${biz.line1} \\n ${biz.city}, ${biz.state_short}`, \n//                         rating: `${(biz.reviewAverage==null) ? 'N/A' : biz.reviewAverage}`,\n//                         cost: `${(biz.reviewCost==null) ? 'N/A' : biz.reviewCost}`,\n//                         count: biz.reviewCount\n//                     },\n//                     geometry: {\n//                         type: \"point\",\n//                         longitude: biz.longitude,\n//                         latitude: biz.latitude\n//                     }\n//                 });\n//             });\n\n//             var businessPopUp = {\n//                 \"title\": \"Business Profile\",\n//                 \"content\": [{\n//                     \"title\": \"{name}\",\n//                     \"type\": \"fields\",\n//                     \"fieldInfos\": [\n//                         {\n//                             \"fieldName\": \"nameLink\",\n//                             \"label\": \"Name\",\n//                         },\n//                         {\n//                             \"fieldName\": \"categories\",\n//                             \"label\": \"Categories\",\n//                         },\n//                         {\n//                             \"fieldName\": \"address\",\n//                             \"label\": \"Address\",\n//                         },\n//                         {\n//                             \"fieldName\": \"telephone\",\n//                             \"label\": \"Telephone\",\n//                         },\n//                         {\n//                             \"fieldName\": \"rating\",\n//                             \"label\": \"Avg. Rating\",\n//                         },\n//                         {\n//                             \"fieldName\": \"cost\",\n//                             \"label\": \"Avg. cost\",\n//                         },\n//                         {\n//                             \"fieldName\": \"count\",\n//                             \"label\": \"# Reviews\",\n//                         },                                                 \n//                     ]\n//                 }]\n//             };\n\n//             var businessLabels = {\n//                 // autocasts as new LabelClass()\n//                 symbol: {\n//                     type: \"text\",\n//                     color: [0,0,0,255],  // black\n//                     font: { family: \"sans-serif\", size: 10, weight: \"normal\" }\n//                 },\n//                 labelPlacement: \"center-right\",\n//                 labelExpressionInfo: {\n//                   expression: \"$feature.name\"\n//                 }\n//             };\n\n//             var featureLayer = new FeatureLayer({\n//                 source: markers,\n//                 renderer: {\n//                     type: \"simple\", // autocasts as new SimpleRenderer()\n//                     symbol: {// autocasts as new SimpleMarkerSymbol()\n//                         type: \"simple-marker\",\n//                         color: [255,0,0],\n//                         outline: { // autocasts as new SimpleLineSymbol()\n//                             style: \"none\",\n//                             color: [255, 255, 255, 0]\n//                         },\n//                         size: 8\n//                     }\n//                 },\n//                 objectIdField: \"ObjectID\", // This must be defined when creating a layer from `Graphic` objects\n//                 fields: [\n//                     {\n//                         name: \"ObjectID\",\n//                         alias: \"ObjectID\",\n//                         type: \"oid\"\n//                     },\n//                     {\n//                         name: \"address\",\n//                         alias: \"address\",\n//                         type: \"string\"\n//                     },\n//                     {\n//                         name: \"nameLink\",\n//                         alias: \"nameLink\",\n//                         type: \"string\"\n//                     },                    \n//                     {\n//                         name: \"name\",\n//                         alias: \"name\",\n//                         type: \"string\"\n//                     },\n//                     {\n//                         name: \"categories\",\n//                         alias: \"categories\",\n//                         type: \"string\"\n//                     },\n//                     {\n//                         name: \"telephone\",\n//                         alias: \"telephone\",\n//                         type: \"string\"\n//                     },\n//                     {\n//                         name: \"rating\",\n//                         alias: \"rating\",\n//                         type: \"string\"\n//                     },\n//                     {\n//                         name: \"cost\",\n//                         alias: \"cost\",\n//                         type: \"string\"               \n//                     },\n//                     {\n//                         name: \"count\",\n//                         alias: \"count\",\n//                         type: \"integer\"               \n//                     }\n//                 ],\n//                 popupTemplate: businessPopUp,\n//                 labelingInfo: [businessLabels]\n//             });\n//             map.layers.add(featureLayer)\n//     });\n// }\n// export default viewMap;\n\n//# sourceURL=webpack:///./src/scripts/maps.js?");

/***/ }),

/***/ "bPrE":
/*!*********************************!*\
  !*** ./src/components/modal.js ***!
  \*********************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("\nlet modal = {\n    delimiters: [\"[[\", \"]]\"],\n    props: {\n        title: {\n            type: String,\n            required: false,\n        },\n        modal_id: {\n            type: String,\n            required: true,\n        }\n    },\n    methods: {\n        emit_hide: function() {\n            this.$emit('modal_hide');\n        },\n        emit_show: function() {\n            this.$emit('modal_show');\n        }\n    },\n    mounted: function(){\n        $(this.$refs.vuemodal).on('hide.bs.modal', this.emit_hide);\n        $(this.$refs.vuemodal).on('show.bs.modal', this.emit_show);\n    },\n    template: `\n    <div>\n        <div class=\"modal fade\" ref=\"vuemodal\" :id=\"modal_id\" tabindex=\"-1\" role=\"dialog\">\n            <div class=\"modal-dialog modal-md\" role=\"document\">\n                <div class=\"modal-content\">\n                    <div class=\"modal-header\">\n                        <h5 class=\"modal-title\">[[ title ]]</h5>\n                        <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\">\n                            <span aria-hidden=\"true\">&times;</span>\n                        </button>\n                    </div>\n                    <div class=\"modal-body px-5\">\n                        <slot name=\"body\"></slot>\n                    </div>\n                    <div class=\"modal-footer\">\n                        <slot name=\"footer\">\n                            <button type=\"button\" class=\"btn btn-secondary\" data-dismiss=\"modal\">Close</button>\n                        </slot>\n                    </div>\n                </div>\n            </div>\n        </div>\n    </div>\n    `\n}\n\n/* harmony default export */ __webpack_exports__[\"a\"] = (modal);\n\n//# sourceURL=webpack:///./src/components/modal.js?");

/***/ }),

/***/ "ejPx":
/*!***************************************!*\
  !*** ./src/components/modal-mixin.js ***!
  \***************************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("/* harmony import */ var _modal__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./modal */ \"bPrE\");\n\n\n\nlet modal_mixin = {\n    components: {\n        'modal': _modal__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"],\n    },\n    delimiters: [\"[[\", \"]]\"],\n    props: {\n        title: {\n            type: String,\n            required: false,\n        },\n        modal_id: {\n            type: String,\n            required: false,\n            default: 'vue_modal'\n        }\n    },\n    methods: {\n        toggleModal: function(){\n            this.show = !this.show;\n            id = `#${this.modal_id}`\n            jQuery(modal_id).modal('toggle');\n        },\n    },\n}\n\n/* harmony default export */ __webpack_exports__[\"a\"] = (modal_mixin);\n\n//# sourceURL=webpack:///./src/components/modal-mixin.js?");

/***/ }),

/***/ "fi43":
/*!*******************************************!*\
  !*** ./src/components/typeahead_mixin.js ***!
  \*******************************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("/* harmony import */ var VueBootstrapTypeahead__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! VueBootstrapTypeahead */ \"OWs1\");\n/* harmony import */ var VueBootstrapTypeahead__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(VueBootstrapTypeahead__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var lodash__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! lodash */ \"LvDl\");\n/* harmony import */ var lodash__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(lodash__WEBPACK_IMPORTED_MODULE_1__);\n\n\n\n\n\nconst typeahead_mixin = {\n    components: {\n        'vue-bootstrap-typeahead': VueBootstrapTypeahead__WEBPACK_IMPORTED_MODULE_0___default.a,\n    },\n    data: function() {\n        return {\n            form: {\n                id: \"\",\n                name: \"\", \n            },\n            typeahead: {\n                suggestions: [],\n                selected: null,\n                include_id: true,\n                name_field: 'name',\n                id_field: 'id',\n            },\n            urls: links,\n        }\n    },\n    methods:{\n        makeQueryUrl: function(){\n            let input = this.form[this.typeahead.name_field];\n            return `${this.urls.autocomplete}?name=${encodeURIComponent(input)}`\n        },\n        getSuggestions: async function(){\n            const res = await fetch(this.makeQueryUrl());\n            const suggestions = await res.json();\n            this.typeahead.suggestions = suggestions;\n        },\n        suggestionSerializer: function(item){\n            return `${item.name}`\n        }\n    },        \n    watch: {\n        'form.name': function(val){\n            const debouncedGetSuggestions = lodash__WEBPACK_IMPORTED_MODULE_1___default.a.debounce(this.getSuggestions, 500);\n            debouncedGetSuggestions();\n        },\n        'typeahead.selected': function(){\n            if (this.typeahead.include_id == true){\n                this.form[this.typeahead.id_field] = this.typeahead.selected.id\n            }\n        }\n    }\n}\n\n/* harmony default export */ __webpack_exports__[\"a\"] = (typeahead_mixin);\n\n//# sourceURL=webpack:///./src/components/typeahead_mixin.js?");

/***/ }),

/***/ "htIL":
/*!****************************!*\
  !*** ./src/scripts/geo.js ***!
  \****************************/
/*! exports provided: getCurrentLocation */
/*! exports used: getCurrentLocation */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"a\", function() { return getCurrentLocation; });\n\nconst getCurrentLocation = () => new Promise((resolve, reject)=> {\n    navigator.geolocation.getCurrentPosition(\n        position => {\n            resolve(position.coords);\n        },\n        error => {\n            reject(error)\n        },\n        {\n            enableHighAccuracy: true,\n            timeout: 1 * 60 * 1000,\n            maximumAge: 5 * 60 * 1000,\n        }\n    );\n});\n\n\n//# sourceURL=webpack:///./src/scripts/geo.js?");

/***/ }),

/***/ "s5Bw":
/*!******************************!*\
  !*** ./src/scripts/forms.js ***!
  \******************************/
/*! exports provided: categoryGet, categoryGetList, getSectorList, makeForm, postForm */
/*! exports used: categoryGet, makeForm, postForm */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"a\", function() { return categoryGet; });\n/* unused harmony export categoryGetList */\n/* unused harmony export getSectorList */\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"b\", function() { return makeForm; });\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"c\", function() { return postForm; });\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! axios */ \"vDqi\");\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_0__);\n\n\nlet category_get_url = '/categorylist';\nlet sector_get_url = '/sectorlist';\n\n\nfunction categoryGet(url, sector, category_id){\n    axios__WEBPACK_IMPORTED_MODULE_0___default.a.get(url, {\n        params: {\n            sector: sector,\n        },\n    })\n    .then(function(response) {\n        updateSelectFieldOptions(response, category_id);\n    })\n    .catch(function(error){\n        console.log(error);\n    });\n}\n\nasync function categoryGetList(sector=null){\n    try {\n        let response = await axios__WEBPACK_IMPORTED_MODULE_0___default.a.get(category_get_url, {\n                        params: {\n                            sector: sector,\n                        },\n        });\n        return response.data;\n    } catch (error){\n        console.log(`error: ${error}`);\n    }\n}\n\nasync function getSectorList(){\n\n    let response = await fetch(sector_get_url)\n    let list = await response.json()\n    return list;\n}\n\nfunction updateSelectFieldOptions(response, id){\n    let selectField = document.getElementById(id);\n    //remove existing options\n    while (selectField.hasChildNodes()){\n        selectField.removeChild(selectField.firstChild);\n    }\n    for (let item of response.data){\n        //append child option element to it with above as content\n        var option = document.createElement('option');\n        option.textContent = item.name;\n        option.value = item.id;\n        selectField.appendChild(option);\n    }    \n}\n\nfunction makeForm(object){\n    let form = new FormData();\n    Object.entries(object).forEach(([k,v]) => form.set(k,v));\n    return form;\n}\n\nfunction postForm(path, params, method='post'){\n    const form = document.createElement('form');\n    form.method = method;\n    form.action = path;\n    \n    for (const key in params){\n        if (params.hasOwnProperty(key)){\n            const hidden_field = document.createElement('input');\n            hidden_field.type = \"hidden\";\n            hidden_field.name = key;\n            hidden_field.value = params[key];\n\n            form.append(hidden_field);\n        }\n    }\n\n    document.body.appendChild(form);\n    form.submit();\n}\n\n\n\n//# sourceURL=webpack:///./src/scripts/forms.js?");

/***/ }),

/***/ "yhse":
/*!**********************************************************!*\
  !*** ./src/components/modal-message-correction-mixin.js ***!
  \**********************************************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("/* harmony import */ var _modal_message_correction__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./modal-message-correction */ \"Moj8\");\n\n\n\nconst modal_message_correction_mixin = {\n    components: {\n        \"modal-message-correction\": _modal_message_correction__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"],\n    },\n    delimiters: ['[[', ']]'],\n    data: {\n        activeBusiness: \"\",\n        form_presets: {\n            csrf_token: csrf,\n            id: \"\",\n            subject: \"\",\n            address: \"\",\n            address_status: \"\",\n            sector: \"\",\n            category: \"\",\n        },\n        urls: {\n            send_message: \"/provider/suggestion\"\n        },\n    },\n    methods: {\n        setMessagePresets: function(event){\n            let source = event.target\n            this.form_presets.id = source.dataset.id\n            this.form_presets.name = source.dataset.subject\n            this.setActiveBusiness(this.form_presets.id);\n            this.form_presets.category = String(this.activeBusiness.category_ids).split(',').map(Number);\n            this.form_presets.sector = Number(this.activeBusiness.sector_ids)\n            this.form_presets.address = {\n                line1: this.activeBusiness.line1,\n                line2: this.activeBusiness.line2,\n                city: this.activeBusiness.city,\n                state: Number(this.activeBusiness.state_id),\n                zip: this.activeBusiness.zip,\n            }\n        },\n        resetFormPresets: function() {\n            Object.keys(this.form_presets).forEach(function(key) {\n                if (key != \"csrf_token\"){\n                    this.form_presets[key] = \"\";\n                }\n            }, this);\n        },\n        setActiveBusiness: function(id) {\n            //to be implemented by individual page\n        }\n    },\n}\n/* harmony default export */ __webpack_exports__[\"a\"] = (modal_message_correction_mixin);\n\n//# sourceURL=webpack:///./src/components/modal-message-correction-mixin.js?");

/***/ }),

/***/ "zIOu":
/*!************************************!*\
  !*** ./src/pages/search/search.js ***!
  \************************************/
/*! exports provided: default */
/*! all exports used */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"oCYn\");\n/* harmony import */ var _components_typeahead_mixin__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../components/typeahead_mixin */ \"fi43\");\n/* harmony import */ var _scripts_maps_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../../scripts/maps.js */ \"S2O+\");\n/* harmony import */ var _scripts_forms_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../../scripts/forms.js */ \"s5Bw\");\n/* harmony import */ var _scripts_geo_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../../scripts/geo.js */ \"htIL\");\n/* harmony import */ var _components_modal_message_correction_mixin__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../../components/modal-message-correction-mixin */ \"yhse\");\n\n\n\n\n\n\n\nvar mapboxgl = __webpack_require__(/*! mapbox-gl/dist/mapbox-gl.js */ \"4ZJM\");\n\nconst mapView = {\n    template: `<div></div>`\n}\n\nconst searchPage = new vue__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"]({\n    el: '#appContent',\n    delimiters: ['[[', ']]'],\n    components:{\n        'map-view': mapView,\n        'vue-bootstrap-typeahead': VueBootstrapTypeahead,\n    },\n    computed:{\n        showManualLocation: function(){\n            return this.form.location == 'manual';\n        },\n        filter: function(){\n            return {\n                sector: this.form.sector,\n                category: this.form.category,\n                location: this.form.location,\n                manual_location: this.form.manual_location,\n                searchRange: this.form.searchRange,\n                name: this.form.name,\n            }\n        }\n    },\n    data: {\n        activeView: 'list',\n        form:{\n            location: form_json.location,\n            manual_location: form_json.manual_location,\n            gpsLat: form_json.gpsLat,\n            gpsLong: form_json.gpsLong,\n            searchRange: form_json.searchRange,\n            sector: form_json.sector,\n            category: form_json.category,\n            name: form_json.name,\n        },\n        map: {\n            show: false,\n            center: mapCenter,\n            container: \"mapContainer\",\n        },\n        searchResults: searchResults,\n        typeahead: {\n            include_id: false,\n        },\n        views: ['list', 'map'],\n        urls: links,\n    },\n    methods: {\n        renderMap: function(){\n            this.map.show = true;\n            let self = this;\n            vue__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"].nextTick(function() {\n                    Object(_scripts_maps_js__WEBPACK_IMPORTED_MODULE_2__[/* default */ \"a\"])(self.map, self.searchResults);\n                });\n        },\n        updateCategory: function(){\n            Object(_scripts_forms_js__WEBPACK_IMPORTED_MODULE_3__[/* categoryGet */ \"a\"])(this.urls.categoryList, this.form.sector, 'category');\n        },\n        makeQueryString: function(){\n            let qs = Object.entries(this.filter).map(function([key,value]){\n                        return `${key}=${encodeURIComponent(value)}`});\n            return `?${qs.join('&')}`;\n        },\n        makeQueryUrl: function(){\n            return this.urls.autocomplete + this.makeQueryString();\n        },\n        setActiveBusiness: function(id) {\n            let b = this.searchResults.filter((business)=> business.id == id)[0]\n            this.activeBusiness = b;\n        }\n    },\n    mixins: [_components_typeahead_mixin__WEBPACK_IMPORTED_MODULE_1__[/* default */ \"a\"], _components_modal_message_correction_mixin__WEBPACK_IMPORTED_MODULE_5__[/* default */ \"a\"]],\n    watch: {\n        'form.location': function(locationSource){\n            if (locationSource == \"gps\"){\n                Object(_scripts_geo_js__WEBPACK_IMPORTED_MODULE_4__[/* getCurrentLocation */ \"a\"])()\n                .then((position) => {\n                    this.form.gpsLat = position.latitude;\n                    this.form.gpsLong = position.longitude;\n                })\n                .catch((error) => {\n                    console.log(`Error: ${error.message}`)\n                })\n            } else {\n                this.form.gpsLat = \"\";\n                this.form.gpsLong = \"\";\n            }\n        },\n    }\n});\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (searchPage);\n\n//# sourceURL=webpack:///./src/pages/search/search.js?");

/***/ })

},[["zIOu","runtime","vendors"]]]);