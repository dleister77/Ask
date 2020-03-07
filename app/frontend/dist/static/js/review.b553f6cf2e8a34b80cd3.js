(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["review"],{

/***/ "ld0O":
/*!************************************!*\
  !*** ./src/pages/review/review.js ***!
  \************************************/
/*! exports provided: default */
/*! all exports used */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"oCYn\");\n\n\n\nconst review = new vue__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"]({\n    el: '#app',\n    delimiters: ['[[', ']]'],\n    data: {},\n    methods: {\n        setRequired: function(){\n            let radio_choices = document.querySelectorAll(\"input[type='radio']\");\n            radio_choices.forEach(element => element.setAttribute(\"required\", true));\n        }\n    },\n    mounted: function(){\n        this.setRequired();\n    }\n});\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (review);\n\n//# sourceURL=webpack:///./src/pages/review/review.js?");

/***/ })

},[["ld0O","runtime","vendors"]]]);