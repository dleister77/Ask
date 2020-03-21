require('jsdom-global')();
global.Vue = require('vue/dist/vue.js');
global.VueTestUtils = require('@vue/test-utils');
global.$ = global.jQuery = require('jquery');