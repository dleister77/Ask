import MessageRead from '../src/components/messages/message-read';

require('jsdom-global')();
const describe = require('mocha').describe;
const it = require('mocha').it;
const assert = require('chai').assert;

const Vue = require('vue/dist/vue.js');
const VueTestUtils = require('@vue/test-utils');

const App = Vue.component('app', MessageRead);


const mountOptions = {
  propsData: {
    message: {
      sender_full_name: 'test_sender',
      timestamp: new Date(Date.UTC(2020, 0, 28, 10, 0, 0)),
      subject: 'test_subject',
      body: 'test_body',
    },
  },
};


describe('displayed message', () => {
  let wrapper;
  before(async () => {
    wrapper = VueTestUtils.mount(App, mountOptions);
  });
  after(() => {
    wrapper.destroy();
  });
  it('check set up', () => {
    assert.isTrue(wrapper.isVueInstance());
  });
  it('should have sender_name', () => {
    assert.isTrue(wrapper.text().includes('test_sender'));
  });
  it('should have subject', () => {
    assert.isTrue(wrapper.text().includes('test_subject'));
  });
  it('should have body', () => {
    assert.isTrue(wrapper.text().includes('test_body'));
  });
  it('should render timestamp correctly', () => {
    assert.isTrue(wrapper.text().includes('January 28, 2020 at 5:00 AM'));
  });
});
