(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["providerProfile"],{

/***/ "ff5E":
/*!*****************************************!*\
  !*** ./src/components/modal-message.js ***!
  \*****************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _form_input_group__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./form-input-group */ \"rdGm\");\n/* harmony import */ var _form_textbox_group__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./form-textbox-group */ \"r7/v\");\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! axios */ \"vDqi\");\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_2__);\n\n\n\n\n\nlet modal_message = {\n    components: {\n        'form-input-group': _form_input_group__WEBPACK_IMPORTED_MODULE_0__[\"default\"],\n        'form-textbox-group': _form_textbox_group__WEBPACK_IMPORTED_MODULE_1__[\"default\"],\n    },\n    data: function(){\n        return {\n            form: {\n                recipient_id:\"\",\n                recipient_name: \"\",\n                subject: \"\",\n                body: \"\",\n            },\n            show: false,\n        }\n    },\n    delimiters: [\"[[\", \"]]\"],\n    props: {\n        csrf: {\n            type: String,\n            required: false,\n        },\n        recipient: {\n            type: Object,\n            required: false,\n        },\n        url: {\n            type: String,\n            required: true,\n        },\n    },\n    methods: {\n        sendMessage: function(){\n            let self = this;\n            const form = new FormData(document.getElementById('message-form'));\n            axios__WEBPACK_IMPORTED_MODULE_2___default.a.post(this.url, form)\n            .then(function(response){\n                if (response.data.status == 'success'){\n                    alert(\"Message sent\");\n                    this.toggleModal()\n                } else {\n                    let message = \"Unabled to send message. Please correct errors:\\n\"\n                    message += response.data.errorMsg.join('\\n');\n                    alert(message);\n                }\n            })\n            .catch(function(error){\n                console.log(error);\n                alert(\"Error: Unable to send message.  Please reload and try again.\")\n            })\n        \n        },\n        toggleModal: function(){\n            this.show = !this.show;\n            $(message-modal).options('toggle');\n        },\n    },\n    template: `\n    <div class=\"modal fade\" id=\"message-modal\" tabindex=\"-1\" role=\"dialog\">\n        <div class=\"modal-dialog modal-md\" role=\"document\">\n            <div class=\"modal-content\">\n                <form id = \"message-form\" v-bind:action=\"url\" method=\"POST\">\n                    <div class=\"modal-header\">\n                        <h5 class=\"modal-title\"><slot></slot></h5>\n                        <button type=\"button\" class=\"close\" data-dismiss=\"modal\" aria-label=\"Close\">\n                            <span aria-hidden=\"true\">&times;</span>\n                        </button>\n                    </div>\n                    <div class=\"modal-body px-5\">\n                        <input v-bind=\"{name: 'csrf_token', value: csrf, type:'hidden'}\">\n                        <input v-bind=\"{name: 'recipient_id', value: recipient.id, type:'hidden'}\">\n                        <form-input-group\n                            v-bind=\"{name: 'recipient', value: recipient.name, readonly: true}\">To\n                        </form-input-group>            \n                        <form-input-group v-bind=\"{name: 'subject'}\">Subject</form-input-group>\n                        <form-textbox-group v-bind=\"{name: 'body'}\">Message Body</form-textbox-group>\n                    </div>\n                    <div class=\"modal-footer\">\n                        <button type=\"button\" class=\"btn btn-secondary\" data-dismiss=\"modal\">Close</button>\n                        <button\n                            class=\"btn btn-primary btn-block submit\"\n                            type=\"submit\"\n                            v-on:click.prevent=\"sendMessage\"\n                        >\n                        Submit\n                    </button>\n                    </div>\n                </form>\n            </div>\n        </div>\n    </div>\n    \n    `\n}\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (modal_message);\n\n//# sourceURL=webpack:///./src/components/modal-message.js?");

/***/ }),

/***/ "qLE9":
/*!***********************************************!*\
  !*** ./src/pages/provider/providerProfile.js ***!
  \***********************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"oCYn\");\n/* harmony import */ var _components_modal_message__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../components/modal-message */ \"ff5E\");\n\n\n\n\nconst profile = new vue__WEBPACK_IMPORTED_MODULE_0__[\"default\"]({\n    el: '#appContent',\n    components: {\n        \"modal-message\": _components_modal_message__WEBPACK_IMPORTED_MODULE_1__[\"default\"],\n    },\n    delimiters: ['[[', ']]'],\n    data: {\n        recipient: {\n            id: \"\",\n            name: \"\"\n        },\n        urls: links,\n        csrf: csrf,\n    },\n    methods: {\n        setRecipient: function(id, name){\n            this.recipient.id = id;\n            this.recipient.name = name;\n        }\n\n    },\n    beforeMount: function(){\n        console.log(\"mounting\")\n\n    },\n    watch: {\n\n    },\n});\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (profile);\n\n//# sourceURL=webpack:///./src/pages/provider/providerProfile.js?");

/***/ }),

/***/ "r7/v":
/*!**********************************************!*\
  !*** ./src/components/form-textbox-group.js ***!
  \**********************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\nlet form_textbox_group = {\n    props: {\n        name: {\n            type: String,\n            required: true,\n        },\n        placeholder: {\n            type: String,\n            required: false,\n        },\n        readonly: {\n            type: Boolean,\n            required: false,\n            default: false,\n        },\n        value: {\n            required: false,\n            default: \"\",\n        },\n        rows: {\n            type: Number,\n            required: false,\n            default: 6,\n        }\n    },\n    methods: {\n        updateValue: function(value){\n            this.$emit('input', value);\n        }   \n    },\n    template: `\n    <div class=\"form-group\">\n        <label\n          v-bind:for=\"name\">\n          <slot></slot>\n        </label>\n        <textarea\n          class=\"form-control\"\n          v-bind=\"$props\"\n          v-bind:id=\"name\"\n          v-on:change=\"updateValue($event.target.value)\">\n        </textarea>\n    </div>\n    `\n};\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (form_textbox_group);\n\n\n//# sourceURL=webpack:///./src/components/form-textbox-group.js?");

/***/ }),

/***/ "rdGm":
/*!********************************************!*\
  !*** ./src/components/form-input-group.js ***!
  \********************************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n\nlet form_input_group = {\n    props: {\n        name: {\n            type: String,\n            required: true,\n        },\n        placeholder: {\n            type: String,\n            required: false,\n        },\n        readonly: {\n            type: Boolean,\n            required: false,\n            default: false,\n        },\n        value: {\n            type: String,\n            required: false,\n            default: \"\",\n        },\n        type: {\n            type: String,\n            required: false,\n            default: \"text\"\n        },\n        autocompleteUrl: {\n            type: String,\n            required: false,\n        }           \n    },\n    methods: {\n        updateValue: function(value){\n            this.$emit('input', value);\n        },\n    },\n    template: `\n    <div class=\"form-group\">\n        <label\n          v-bind:for=\"name\">\n          <slot></slot>\n        </label>\n        <input\n          class=\"form-control\"\n          v-bind=\"$props\"\n          v-bind:id=\"name\"\n          v-on:change=\"updateValue($event.target.value)\">\n        </input>\n    </div>\n    `,\n}\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (form_input_group);\n\n//# sourceURL=webpack:///./src/components/form-input-group.js?");

/***/ })

},[["qLE9","runtime","vendors"]]]);