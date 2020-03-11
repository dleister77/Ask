(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["userProfile"],{

/***/ "6a2F":
/*!***************************************!*\
  !*** ./src/pages/user/userProfile.js ***!
  \***************************************/
/*! exports provided: default */
/*! all exports used */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"oCYn\");\n/* harmony import */ var _components_modal_message_user_mixin__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../../components/modal-message-user-mixin */ \"7vub\");\n\n\n\n\nconst user = new vue__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"]({\n    el: '#appContent',\n    mixins: [_components_modal_message_user_mixin__WEBPACK_IMPORTED_MODULE_1__[/* default */ \"a\"]],\n});\n\n/* harmony default export */ __webpack_exports__[\"default\"] = (user);\n\n//# sourceURL=webpack:///./src/pages/user/userProfile.js?");

/***/ }),

/***/ "7vub":
/*!****************************************************!*\
  !*** ./src/components/modal-message-user-mixin.js ***!
  \****************************************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("/* harmony import */ var _modal_message_user__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./modal-message-user */ \"ewpM\");\n\n\n\nconst modal_message_user_mixin = {\n    components: {\n        \"modal-message-user\": _modal_message_user__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"],\n    },\n    delimiters: ['[[', ']]'],\n    data: {\n        form_presets: {\n            csrf_token: csrf,\n            recipient_id: \"\",\n            recipient_name: \"\",\n            subject: \"\",\n        },\n        urls: {\n            send_message: \"/message/send\"\n        },\n    },\n    methods: {\n        setMessagePresets: function(event){\n            let source = event.target\n            this.form_presets.recipient_id = source.dataset.id\n            this.form_presets.recipient_name = source.dataset.name\n            this.form_presets.subject = source.dataset.subject\n        },\n        resetFormPresets: function() {\n            Object.keys(this.form_presets).forEach(function(key) {\n                if (key != \"csrf_token\"){\n                    this.form_presets[key] = \"\";\n                }\n            }, this);\n        }\n    },\n}\n/* harmony default export */ __webpack_exports__[\"a\"] = (modal_message_user_mixin);\n\n//# sourceURL=webpack:///./src/components/modal-message-user-mixin.js?");

/***/ }),

/***/ "KCvK":
/*!*****************************************!*\
  !*** ./src/components/error-message.js ***!
  \*****************************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("let ErrorMessage = {\n    props: {\n        field: Object,\n        validator: String,\n    },\n    computed: {\n        isInvalid(){\n            return !this.field[this.validator] && this.field[\"$dirty\"];\n        }\n    },\n    template: \n           `<div>\n                <small v-if='isInvalid' class=\"form-error-message\">\n                <slot></slot>\n                </small>\n            </div>\n            `\n}\n\n/* harmony default export */ __webpack_exports__[\"a\"] = (ErrorMessage);\n\n//# sourceURL=webpack:///./src/components/error-message.js?");

/***/ }),

/***/ "NZ/9":
/*!*********************************************!*\
  !*** ./src/components/form-message-user.js ***!
  \*********************************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("/* harmony import */ var vue__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! vue */ \"oCYn\");\n/* harmony import */ var vuelidate__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! vuelidate */ \"Hc5T\");\n/* harmony import */ var vuelidate__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(vuelidate__WEBPACK_IMPORTED_MODULE_1__);\n/* harmony import */ var _form_input_group__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./form-input-group */ \"rdGm\");\n/* harmony import */ var _form_textbox__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./form-textbox */ \"P1Lo\");\n/* harmony import */ var _form_input__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./form-input */ \"iE8x\");\n/* harmony import */ var vuelidate_lib_validators_required__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! vuelidate/lib/validators/required */ \"1PTn\");\n/* harmony import */ var vuelidate_lib_validators_required__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(vuelidate_lib_validators_required__WEBPACK_IMPORTED_MODULE_5__);\n\n\n\n\n\n\n\n\n\nvue__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"].use(vuelidate__WEBPACK_IMPORTED_MODULE_1___default.a);\n\nlet form_message_user = {\n    components: {\n        'form-input': _form_input__WEBPACK_IMPORTED_MODULE_4__[/* default */ \"a\"],\n        'form-input-group': _form_input_group__WEBPACK_IMPORTED_MODULE_2__[/* default */ \"a\"],\n        'form-textbox': _form_textbox__WEBPACK_IMPORTED_MODULE_3__[/* default */ \"a\"],\n    },\n    data: function(){\n        return {\n            form: {\n                csrf_token: \"\",\n                recipient_id: \"\",\n                recipient_name: \"\",\n                subject: \"\",\n                body: \"\",\n            },\n        }\n    },\n    delimiters: [\"[[\", \"]]\"],\n    props: {\n        form_presets: {\n            type: Object,\n            required: false,\n        },\n        url: {\n            type: String,\n            required: true,\n        },\n        reset_form: {\n            type: Boolean,\n            required: false,\n        }\n    },\n    validations: {\n        form: {\n            recipient_id: {\n                required: (vuelidate_lib_validators_required__WEBPACK_IMPORTED_MODULE_5___default()),\n            },\n            recipient_name: {\n                required: (vuelidate_lib_validators_required__WEBPACK_IMPORTED_MODULE_5___default()),\n            },\n            subject: {\n                required: (vuelidate_lib_validators_required__WEBPACK_IMPORTED_MODULE_5___default()),\n            },\n            body: {\n                required: (vuelidate_lib_validators_required__WEBPACK_IMPORTED_MODULE_5___default()),\n            }\n        },\n    },\n    methods: {\n        resetForm: function() {\n            this.$v.$reset();\n            Object.keys(this.form).forEach((key)=> this.form[key]=\"\");\n        },\n    },\n    watch: {\n        'form_presets': {\n            handler: function(new_val) {\n            Object.entries(this.form_presets).forEach(([key,value])=>this.form[key]=value);\n            },\n            deep: true,\n        },\n        'reset_form': function(new_val) {\n            if (new_val==true) {\n                this.resetForm();\n                this.$emit('form_is_reset')\n            }\n        },\n        '$v.$invalid': function(new_val) {\n            let is_valid = !new_val;\n            this.$emit('form_is_valid', is_valid);\n        }        \n    },\n    template: `\n    <div>\n        <form id = \"message-form\" v-bind:action=\"url\" method=\"POST\">\n            <input name=\"csrf_token\" type=\"hidden\" :value=\"form_presets.csrf_token\">\n            <input name='recipient_id' type=\"hidden\" :value=\"form_presets.recipient_id\">\n            <div class=\"form-group\">\n                <form-input\n                name=\"recipient\"\n                    v-model.trim=\"$v.form.recipient_name.$model\"\n                    :readonly=true\n                    :validator=$v.form.recipient_name>\n                    To\n                </form-input>\n            </div>\n            <div class=\"form-group\">\n                <form-input\n                    name='subject'\n                    v-model.trim=\"$v.form.subject.$model\"\n                    :validator=\"$v.form.subject\">\n                    Subject\n                </form-input>\n            </div>\n            <div class=\"form-group\">\n                <form-textbox\n                    name='body'\n                    v-model.trim=\"$v.form.body.$model\"\n                    :validator=\"$v.form.body\">\n                    Message Body\n                </form-textbox>\n            </div>\n        </form>\n    </div>\n    \n    `\n}\n/* harmony default export */ __webpack_exports__[\"a\"] = (form_message_user);\n\n//# sourceURL=webpack:///./src/components/form-message-user.js?");

/***/ }),

/***/ "P1Lo":
/*!****************************************!*\
  !*** ./src/components/form-textbox.js ***!
  \****************************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("/* harmony import */ var _error_message__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./error-message */ \"KCvK\");\n\n\nlet FormInput = {\n    components: {\n        'error-message': _error_message__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"],\n    },\n    props: {\n        name: {\n            type: String,\n            required: true,\n        },\n        placeholder: {\n            type: String,\n            required: false,\n        },\n        readonly: {\n            type: Boolean,\n            required: false,\n            default: false,\n        },\n        value: {\n            type: String,\n            required: false,\n            default: \"\",\n        },\n        type: {\n            type: String,\n            required: false,\n            default: \"text\"\n        },\n        required: {\n            type: Boolean,\n            required: false,\n            default: true,\n        },\n        validator: {\n            type: Object,\n            required: false,\n        },\n        server_side_errors: {\n            type: Array,\n            required: false,\n        },\n        rows: {\n            type: Number,\n            required: false,\n            default: 6,\n        }\n    },\n    computed: {\n      filtered_server_side_errors() {\n        if (this.value != \"\" && this.server_side_errors != undefined){\n          let errors = this.server_side_errors.filter(function(error){\n            return !error.includes(\"require\")\n          });\n          return errors;\n        } else {\n          return this.server_side_errors;\n        }\n      },\n      error_class: function() {\n        if (this.validator != undefined && this.validator.$error){\n          return 'form-error'\n        }\n      }\n    },\n    methods: {\n        updateValue: function(value){\n            this.$emit('input', value);\n        },\n    },\n    template: `\n    <div>\n        <label\n          v-bind:for=\"name\">\n          <slot></slot>\n        </label>\n        <small v-if=\"!required\" class=\"text-muted font-italic\">optional</small>\n        <textarea\n          class=\"form-control\"\n          :class=\"error_class\"\n          v-bind=\"$props\"\n          v-bind:id=\"name\"\n          v-on:change=\"updateValue($event.target.value)\">\n        </textarea>\n        <error-message\n            v-if=\"required\"\n            :field=\"validator\"\n            validator=\"required\">\n            <slot></slot> is required.\n        </error-message>\n        <template v-for=\"error in filtered_server_side_errors\">\n          <small class=\"form-error-message\">\n          {{ error }}\n          </small>\n        </template>\n    </div>\n    `,\n}\n\n/* harmony default export */ __webpack_exports__[\"a\"] = (FormInput);\n\n//# sourceURL=webpack:///./src/components/form-textbox.js?");

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
eval("/* harmony import */ var _modal__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./modal */ \"bPrE\");\n\n\n\nlet modal_mixin = {\n    components: {\n        'modal': _modal__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"],\n    },\n    delimiters: [\"[[\", \"]]\"],\n    props: {\n        title: {\n            type: String,\n            required: false,\n        },\n        modal_id: {\n            type: String,\n            required: false,\n            default: 'vue_modal'\n        }\n    },\n    methods: {\n        toggleModal: function(){\n            this.show = !this.show;\n            let id = `#${this.modal_id}`;\n            jQuery(id).modal('toggle');\n        },\n    },\n}\n\n/* harmony default export */ __webpack_exports__[\"a\"] = (modal_mixin);\n\n//# sourceURL=webpack:///./src/components/modal-mixin.js?");

/***/ }),

/***/ "ewpM":
/*!**********************************************!*\
  !*** ./src/components/modal-message-user.js ***!
  \**********************************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("/* harmony import */ var _modal_mixin__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./modal-mixin */ \"ejPx\");\n/* harmony import */ var _form_message_user__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./form-message-user */ \"NZ/9\");\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! axios */ \"vDqi\");\n/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_2__);\n\n\n\n\n\n\nlet modal_message_user = {\n    components: {\n        'form-message-user': _form_message_user__WEBPACK_IMPORTED_MODULE_1__[/* default */ \"a\"],\n    },\n    mixins: [_modal_mixin__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"]],\n    data: function(){\n        return {\n            reset_form: false,\n            form_is_valid: false,\n        }\n    },\n    delimiters: [\"[[\", \"]]\"],\n    props: {\n        form_presets: {\n            type: Object,\n            required: false,\n        },\n        url: {\n            type: String,\n            required: true,\n        },\n    },\n    methods: {\n        resetFormPresets: function() {\n            this.reset_form = false;\n            this.$emit('reset_form_presets');\n        },\n        setValidity: function(form_is_valid_payload) {\n            this.form_is_valid = form_is_valid_payload;\n        },\n        sendMessage: function(){\n            if (!this.form_is_valid){\n                alert(\"Please correct errors and resubmit\")\n            } else {\n                let self = this;\n                const form = new FormData(document.getElementById('message-form'));\n                axios__WEBPACK_IMPORTED_MODULE_2___default.a.post(this.url, form)\n                .then(function(response){\n                    if (response.data.status == 'success'){\n                        alert(\"Message sent\");\n                        self.toggleModal()\n                    } else {\n                        let message = \"Unabled to send message. Please correct errors:\\n\"\n                        message += response.data.errorMsg.join('\\n');\n                        alert(message);\n                    }\n                })\n                .catch(function(error){\n                    console.log(error);\n                    alert(\"Error: Unable to send message.  Please reload and try again.\")\n                })\n            }\n        },\n    },\n    template: `\n    <div>\n        <modal\n            title=\"Send Message\"\n            :modal_id=\"modal_id\"\n            @modal_hide=\"reset_form=true\">\n            <template v-slot:body>\n                <form-message-user\n                    :form_presets=\"form_presets\"\n                    :url=\"url\"\n                    :reset_form=\"reset_form\"\n                    @form_is_reset=\"resetFormPresets\"\n                    @form_is_valid=\"setValidity\">\n                </form-message-user>\n            </template>\n            <template v-slot:footer>           \n                <button\n                    class=\"btn btn-primary btn-block submit\"\n                    type=\"submit\"\n                    v-on:click.prevent=\"sendMessage\">\n                    Submit\n                </button>\n            </template>\n        </modal>\n    </div>\n    \n    `\n}\n\n/* harmony default export */ __webpack_exports__[\"a\"] = (modal_message_user);\n\n//# sourceURL=webpack:///./src/components/modal-message-user.js?");

/***/ }),

/***/ "iE8x":
/*!**************************************!*\
  !*** ./src/components/form-input.js ***!
  \**************************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("/* harmony import */ var _error_message__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./error-message */ \"KCvK\");\n\n\nlet FormInput = {\n    components: {\n        'error-message': _error_message__WEBPACK_IMPORTED_MODULE_0__[/* default */ \"a\"],\n    },\n    props: {\n        name: {\n            type: String,\n            required: true,\n        },\n        placeholder: {\n            type: String,\n            required: false,\n        },\n        readonly: {\n            type: Boolean,\n            required: false,\n            default: false,\n        },\n        value: {\n            type: String,\n            required: false,\n            default: \"\",\n        },\n        type: {\n            type: String,\n            required: false,\n            default: \"text\"\n        },\n        required: {\n            type: Boolean,\n            required: false,\n            default: true,\n        },\n        validator: {\n            type: Object,\n            required: false,\n        },\n        server_side_errors: {\n            type: Array,\n            required: false,\n        }\n    },\n    computed: {\n      filtered_server_side_errors() {\n        if (this.value != \"\" && this.server_side_errors != undefined){\n          let errors = this.server_side_errors.filter(function(error){\n            return !error.includes(\"require\")\n          });\n          return errors;\n        } else {\n          return this.server_side_errors;\n        }\n      },\n      error_class: function() {\n        if (this.validator != undefined && this.validator.$error){\n          return 'form-error'\n        }\n      }\n    },\n    methods: {\n        updateValue: function(value){\n            this.$emit('input', value);\n        },\n    },\n    template: `\n    <div class=\"form-group\">\n        <label\n          v-bind:for=\"name\">\n          <slot></slot>\n        </label>\n        <small v-if=\"!required\" class=\"text-muted font-italic\">optional</small>\n        <input\n          class=\"form-control\"\n          :class=\"error_class\"\n          v-bind=\"$props\"\n          v-bind:id=\"name\"\n          v-on:change=\"updateValue($event.target.value)\">\n        </input>\n        <error-message\n            v-if=\"required\"\n            :field=\"validator\"\n            validator=\"required\">\n            <slot></slot> is required.\n        </error-message>\n        <slot name=\"errors\"></slot>\n        <template v-for=\"error in filtered_server_side_errors\">\n          <small class=\"form-error-message\">\n          {{ error }}\n          </small>\n        </template>\n    </div>\n    `,\n}\n\n/* harmony default export */ __webpack_exports__[\"a\"] = (FormInput);\n\n//# sourceURL=webpack:///./src/components/form-input.js?");

/***/ }),

/***/ "rdGm":
/*!********************************************!*\
  !*** ./src/components/form-input-group.js ***!
  \********************************************/
/*! exports provided: default */
/*! exports used: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
eval("\nlet form_input_group = {\n    props: {\n        name: {\n            type: String,\n            required: true,\n        },\n        placeholder: {\n            type: String,\n            required: false,\n        },\n        readonly: {\n            type: Boolean,\n            required: false,\n            default: false,\n        },\n        value: {\n            type: String,\n            required: false,\n            default: \"\",\n        },\n        type: {\n            type: String,\n            required: false,\n            default: \"text\"\n        },\n        autocompleteUrl: {\n            type: String,\n            required: false,\n        }           \n    },\n    methods: {\n        updateValue: function(value){\n            this.$emit('input', value);\n        },\n    },\n    template: `\n    <div class=\"form-group\">\n        <label\n          v-bind:for=\"name\">\n          <slot></slot>\n        </label>\n        <input\n          class=\"form-control\"\n          v-bind=\"$props\"\n          v-bind:id=\"name\"\n          v-on:change=\"updateValue($event.target.value)\">\n        </input>\n    </div>\n    `,\n}\n\n/* harmony default export */ __webpack_exports__[\"a\"] = (form_input_group);\n\n//# sourceURL=webpack:///./src/components/form-input-group.js?");

/***/ })

},[["6a2F","runtime","vendors"]]]);