(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["friendAdd"],{

/***/ "OWs1":
/*!****************************************!*\
  !*** external "VueBootstrapTypeahead" ***!
  \****************************************/
/*! no static exports found */
/*! exports used: default */
/***/ (function(module, exports) {

eval("module.exports = VueBootstrapTypeahead;\n\n//# sourceURL=webpack:///external_%22VueBootstrapTypeahead%22?");

/***/ }),

/***/ "dyp3":
/*!***************************************!*\
  !*** ./src/pages/friend/friendAdd.js ***!
  \***************************************/
/*! exports provided: default */
/*! all exports used */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"oCYn\");\n/* harmony import */ var _components_typeahead_mixin__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../components/typeahead_mixin */ \"fi43\");\n\n\n\n\nconst friendAdd = new vue__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"]({\n    el: '#app',\n    delimiters: ['[[', ']]'],\n    mixins: [_components_typeahead_mixin__WEBPACK_IMPORTED_MODULE_1__[/* default */ \"a\"]],\n    data: {\n        urls: links,\n        typeahead: {\n            include_id: false,\n        }\n    },\n    methods: {\n        suggestionSerializer: function(person){\n            return `${person.first_name} ${person.last_name}, ${person.city} ${person.state}`\n        }\n    },\n});\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (friendAdd);\n\n//# sourceURL=webpack:///./src/pages/friend/friendAdd.js?");

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

/***/ })

},[["dyp3","runtime","vendors"]]]);