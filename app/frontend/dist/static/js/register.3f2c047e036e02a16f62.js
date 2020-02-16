(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["register"],{

/***/ "3AHF":
/*!****************************************!*\
  !*** ./src/pages/register/register.js ***!
  \****************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"oCYn\");\n/* harmony import */ var vuelidate__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! vuelidate */ \"Hc5T\");\n/* harmony import */ var vuelidate__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(vuelidate__WEBPACK_IMPORTED_MODULE_1__);\n/* harmony import */ var vuelidate_lib_validators_required__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! vuelidate/lib/validators/required */ \"1PTn\");\n/* harmony import */ var vuelidate_lib_validators_required__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(vuelidate_lib_validators_required__WEBPACK_IMPORTED_MODULE_2__);\n/* harmony import */ var vuelidate_lib_validators_sameAs__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! vuelidate/lib/validators/sameAs */ \"tsu9\");\n/* harmony import */ var vuelidate_lib_validators_sameAs__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(vuelidate_lib_validators_sameAs__WEBPACK_IMPORTED_MODULE_3__);\n\n\n\n\n\n\nvue__WEBPACK_IMPORTED_MODULE_0__[\"default\"].use(vuelidate__WEBPACK_IMPORTED_MODULE_1___default.a);\n\n\nconst register = new vue__WEBPACK_IMPORTED_MODULE_0__[\"default\"]({\n    el: '#app',\n    delimiters: ['[[', ']]'],\n    data: {\n        form: {\n            password: \"\",\n            confirmation: \"\",\n        }\n    },\n    validations: {\n        form: {\n            password: {\n                required: (vuelidate_lib_validators_required__WEBPACK_IMPORTED_MODULE_2___default()),\n            },\n            confirmation: {\n                required: (vuelidate_lib_validators_required__WEBPACK_IMPORTED_MODULE_2___default()),\n                matches: vuelidate_lib_validators_sameAs__WEBPACK_IMPORTED_MODULE_3___default()('password'),\n            },\n        }\n    },\n    methods: {\n\n    },\n\n});\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (register);\n\n//# sourceURL=webpack:///./src/pages/register/register.js?");

/***/ })

},[["3AHF","runtime","vendors"]]]);