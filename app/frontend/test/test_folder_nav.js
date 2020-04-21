import { BootstrapVue } from 'bootstrap-vue';

import FolderNav from '../src/components/folder-nav';

require('jsdom-global')();
const describe = require('mocha').describe;
const it = require('mocha').it;
const beforeEach = require('mocha').beforeEach;
const afterEach = require('mocha').afterEach;
const assert = require('chai').assert

const Vue = require('vue/dist/vue.js');
const VueTestUtils = require('@vue/test-utils');

const App = Vue.component('app', FolderNav);

Vue.use(BootstrapVue);

const mountOptions = {
  propsData: {
    eventSignal: {
      updateActive: 'update-active-message',
      newMessage: 'new-message',
      backToLast: 'back-to-last',
      replyToMessage: 'reply-to-message',
      moveMessage: 'move-message',
    },
    folderIsVisible: true,
    messageIsVisible: false,
    moveLinksVisible: false,
    newMessageIsVisible: false,
    messagePosition: {
      current: null,
      last: 3,
    },
    urls: {
      view_inbox: '/message/folder/inbox',
      view_sent: '/message/folder/sent',
      view_archive: '/message/folder/archive',
      view_trash: '/message/folder/trash',
    },
  },
};

describe('check instance', () => {
  let wrapper=VueTestUtils.mount(App, mountOptions);
  it('check that its a vue instance', () => {
    assert.isTrue(wrapper.isVueInstance());
  });
  wrapper.destroy();
});

describe('visible links', () => {
  let wrapper;
  const refsToTest = [
    'folder-list', 'new-message', 'back-button', 'previous-message',
    'next-message', 'reply-to', 'move-links-delete', 'move-links-archive',
  ];
  describe('show set to true', async () => {
    before(async () => {
      wrapper = VueTestUtils.mount(App, mountOptions);
      wrapper.setProps({ folderIsVisible: true, messageIsVisible: true, moveLinksVisible: true });
      await Vue.nextTick();
    });
    after(() => {
      wrapper.destroy();
    });
    it('check set up', () => {
      assert.isTrue(wrapper.vm.$props.folderIsVisible);
      assert.isTrue(wrapper.vm.$props.messageIsVisible);
      assert.isTrue(wrapper.vm.$props.moveLinksVisible);
    });

    refsToTest.forEach((item) => {
      it(item, () => {
        assert.isTrue(wrapper.find({ ref: item }).exists());
      });
    });
  });

  describe('show set to false', async () => {
    before(async () => {
      wrapper = VueTestUtils.mount(App, mountOptions);
      const props = {
        folderIsVisible: false,
        messageIsVisible: false,
        moveLinksVisible: false,
      };
      wrapper.setProps(props);
      await Vue.nextTick();
    });
    after(() => {
      wrapper.destroy();
    });
    it('check set up', () => {
      assert.isNotTrue(wrapper.vm.$props.folderIsVisible);
      assert.isNotTrue(wrapper.vm.$props.messageIsVisible);
      assert.isNotTrue(wrapper.vm.$props.moveLinksVisible);
    });
    refsToTest.forEach((item) => {
      it(item, () => {
        assert.isNotTrue(wrapper.find({ ref: item }).exists());
      });
    });
  });
});
