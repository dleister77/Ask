import NavListButton from '../src/components/nav-list-button';

require('jsdom-global')();

const describe = require('mocha').describe;
const it = require('mocha').it;
const assert = require('chai').assert
const Vue = require('vue/dist/vue.js');
const VueTestUtils = require('@vue/test-utils');

const App = Vue.component('app', NavListButton);

const mountOptions = {
  propsData: {
    eventSignal: 'testsignal',
  },
};

const wrapper = VueTestUtils.mount(App, mountOptions);

wrapper.find('button').trigger('click');

describe('nav list button', () => {
  it('should emit test-signal when button is clicked', () => {
    assert.equal(wrapper.emitted().testsignal.length, 1);
  });
});
