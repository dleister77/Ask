(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["userProfile"],{

/***/ "6a2F":
/*!***************************************!*\
  !*** ./src/pages/user/userProfile.js ***!
  \***************************************/
/*! exports provided: default */
/*! all exports used */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"oCYn\");\n/* harmony import */ var _components_modal_message_mixin__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../components/modal-message-mixin */ \"9TPT\");\n\n\n\n\nconst user = new vue__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"]({\n    el: '#appContent',\n    mixins: [_components_modal_message_mixin__WEBPACK_IMPORTED_MODULE_1__[/* default */ \"a\"]],\n});\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (user);\n\n//# sourceURL=webpack:///./src/pages/user/userProfile.js?");

/***/ }),

/***/ "9TPT":
/*!***********************************************!*\
  !*** ./src/components/modal-message-mixin.js ***!
  \***********************************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("/* harmony import */ var _modal_message__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./modal-message */ \"ff5E\");\n\n\n\nconst modal_message_mixin = {\n    components: {\n        \"modal-message\": _modal_message__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"],\n    },\n    delimiters: ['[[', ']]'],\n    data: {\n        recipient: {\n            id: \"\",\n            name: \"\",\n            subject: \"\",\n        },\n        urls: {\n            send_message: \"/message/send\"\n        },\n        csrf: csrf,\n    },\n    methods: {\n        setRecipient: function(event){\n            let source = event.target\n            this.recipient.id = source.dataset.id\n            this.recipient.name = source.dataset.name\n            this.recipient.subject = source.dataset.subject\n        }\n\n    },\n}\n/* harmony default export */ __webpack_exports__[\"a\"] = (modal_message_mixin);\n\n//# sourceURL=webpack:///./src/components/modal-message-mixin.js?");

/***/ }),

/***/ "ff5E":
/*!*****************************************!*\
  !*** ./src/components/modal-message.js ***!
  \*****************************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, exports) {

eval("throw new Error(\"Module parse failed: Unexpected token (96:12)\\nYou may need an appropriate loader to handle this file type, currently no loaders are configured to process this file. See https://webpack.js.org/concepts#loaders\\n|         },\\n|     },\\n>     mounted () {\\n|         $(this.$refs.vuemodal).on('hide.bs.modal', this.resetMessage);\\n|     },\");\n\n//# sourceURL=webpack:///./src/components/modal-message.js?");

/***/ })

},[["6a2F","runtime","vendors"]]]);