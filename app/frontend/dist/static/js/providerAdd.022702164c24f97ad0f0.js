(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["providerAdd"],{

/***/ "luZg":
/*!*******************************************!*\
  !*** ./src/pages/provider/providerAdd.js ***!
  \*******************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"oCYn\");\n/* harmony import */ var _scripts_forms_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../scripts/forms.js */ \"s5Bw\");\n\n\n\n\nconst providerAdd = new vue__WEBPACK_IMPORTED_MODULE_0__[\"default\"]({\n    el: '#app',\n    delimiters: ['[[', ']]'],\n    data: {\n        form:{\n            name:\"\",\n            sector: 1,\n            category: [],\n            email:\"\",\n            website: \"\",\n            telephone: \"\",\n            addressUnknown:false,\n            line1: \"\",\n            line2:\"\",\n            city:\"\",\n            zip:\"\",\n            state: \"\",\n\n        },\n        show: {\n            partial_address: false,\n        },\n        urls: links,\n    },\n    methods: {\n        updateCategory: function(){\n            Object(_scripts_forms_js__WEBPACK_IMPORTED_MODULE_1__[\"categoryGet\"])(this.urls.categoryList, this.form.sector, 'category');\n            this.form.category = [];\n        },\n    },\n    mounted: function(){\n        const select = document.getElementById(\"category\");\n        this.form.category.push(select.firstElementChild.value);\n    },\n    watch: {\n        'form.addressUnknown': function(){\n            this.show.partial_address = ! this.show.partial_address;\n        },\n    }\n});\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (providerAdd);\n\n//# sourceURL=webpack:///./src/pages/provider/providerAdd.js?");

/***/ }),

/***/ "s5Bw":
/*!******************************!*\
  !*** ./src/scripts/forms.js ***!
  \******************************/
/*! exports provided: categoryGet */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, \"categoryGet\", function() { return categoryGet; });\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! axios */ \"vDqi\");\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_0__);\n\n\nfunction categoryGet(url, sector, category_id){\n    axios__WEBPACK_IMPORTED_MODULE_0___default.a.get(url, {\n        params: {\n            sector: sector,\n        },\n    })\n    .then(function(response) {\n        updateSelectFieldOptions(response, category_id);\n    })\n    .catch(function(error){\n        console.log(error);\n    });\n}\n\nfunction updateSelectFieldOptions(response, id){\n    let selectField = document.getElementById(id);\n    //remove existing options\n    while (selectField.hasChildNodes()){\n        selectField.removeChild(selectField.firstChild);\n    }\n    for (let item of response.data){\n        //append child option element to it with above as content\n        var option = document.createElement('option');\n        option.textContent = item.name;\n        option.value = item.id;\n        selectField.appendChild(option);\n    }    \n}\n\n\n//# sourceURL=webpack:///./src/scripts/forms.js?");

/***/ })

},[["luZg","runtime","vendors"]]]);