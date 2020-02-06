import nav_list_button from '../app/static/components/nav-list-button.js';

require('jsdom-global')();


const describe = require('mocha').describe;
const it = require('mocha').it;
const assert = require('chai').assert
const Vue = require('vue/dist/vue.js');
const VueTestUtils = require('@vue/test-utils');

const App = Vue.component('app', nav_list_button);

const wrapper = VueTestUtils.mount(App,{
    propsData:{
        eventSignal: 'testsignal'
    }
});

wrapper.find('button').trigger('click');

describe('nav list button', function(){
  it('should emit test-signal when button is clicked', function(){
      assert.equal(wrapper.emitted().testsignal.length,1);
    });
  });