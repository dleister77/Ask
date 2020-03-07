(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["header"],{

/***/ "6Z/Q":
/*!*******************************************!*\
  !*** ./src/pages/layout/header/header.js ***!
  \*******************************************/
/*! no exports provided */
/*! all exports used */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"oCYn\");\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! axios */ \"vDqi\");\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_1__);\n\n\n\n\nconst topNavbar = new vue__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"]({\n    el: '#topNavbar',\n    data: {\n        unreadCount: initial_unread_count,\n        unready_url: unread_url,\n    },\n    delimiters: ['[[',']]'],\n    methods: {\n        setUpTimer: function(){\n            let intervalID = setInterval(this.getUnread, 60000)\n        },\n        getUnread: function(url){\n            let self = this;\n            axios__WEBPACK_IMPORTED_MODULE_1___default.a.get(this.unread_url)\n                .then(function(response){\n                    self.unreadCount = response.data.unread_count;\n                })\n                .catch(function(error){\n                    console.log(error);\n                })\n        }\n        \n    },\n    created: function(){\n        this.setUpTimer();\n    }\n});\n\n//# sourceURL=webpack:///./src/pages/layout/header/header.js?");

/***/ })

},[["6Z/Q","runtime","vendors"]]]);