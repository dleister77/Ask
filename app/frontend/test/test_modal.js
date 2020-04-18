
import baseModal from '../src/components/modals/base-modal';

const describe = require('mocha').describe;
const it = require('mocha').it;
const assert = require('chai').assert
const sinon = require('sinon');

const App = Vue.component('app', baseModal);

require('bootstrap');


const mountOptions = {
  propsData: {
    modal_id: 'test-modal',
    title: 'My Test Modal',
    show_modal: false,
    hide_modal: false,
  },
};

// TODO FIX JS TESTING EVENT NOT SHOWING ISSUE
describe('modal', () => {
  let wrapper;
  beforeEach(() => {
    wrapper = VueTestUtils.mount(App, mountOptions);
  });
  afterEach(() => {
    wrapper.destroy();
  });
  describe('check instance', () => {
    it('check that message modal is a vue instance', () => {
      assert.isTrue(wrapper.isVueInstance());
    });
  });
  describe('check manual hide and show', () => {
    it('should show when show_modal set to true', async () => {
      wrapper.setProps({ show_modal: true });
      assert.equal(wrapper.vm.show_modal, true, 'prop not set');
      await Vue.nextTick();
      assert.equal(wrapper.emitted().modal_show.length, 1, 'show event not emitted');
    });
    it('should hide when hide_modal set to true', async () => {
      wrapper.setProps({ hide_modal: true });
      assert.equal(wrapper.vm.hide_modal, true, 'prop not set');
      await Vue.nextTick();
      assert.equal(wrapper.emitted().modal_hide.length, 1, 'hide event not emitted');
    });
  });
  describe('jQuery eventListeners', () => {
    describe('show', () => {
      it('emit modal show', async () => {
        $(wrapper.vm.$refs.vuemodal).modal('show');
        await Vue.nextTick();
        assert.equal(wrapper.emitted().modal_show.length, 1, 'modal show not emitted');
      });
    });
    describe('hide', () => {
      it('emit modal hide', async () => {
        $(wrapper.vm.$refs.vuemodal).modal('hide');
        await Vue.nextTick();
        assert.equal(wrapper.emitted().modal_hide.length, 1, 'modal hide not emitted');
        assert.equal(wrapper.emitted().modal_is_hidden.length, 1, 'modal hidden not emitted');
      });
    });
  });
});
