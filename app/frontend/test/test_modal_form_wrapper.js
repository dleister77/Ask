
import ModalFormWrapper from '../src/components/modals/modal-form-wrapper';
import BaseModal from '../src/components/modals/base-modal';

const { describe } = require('mocha');
const { it } = require('mocha');
const { assert } = require('chai');

const App = Vue.component('app', ModalFormWrapper);

require('bootstrap');


const mountOptions = {
  propsData: {
    title: 'test-modal',
    url: 'localhost:5000/test',
  },
};


describe('modal form wrapper', () => {
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
  describe('check modal hide functions', () => {
    it('should change reset form values to true', () => {
      assert.isFalse(wrapper.vm.reset_form_values);
      const bm = wrapper.find(BaseModal);
      bm.vm.$emit('modal_hide');
      assert.equal(bm.emitted().modal_hide.length, 1);
      assert.isTrue(wrapper.vm.$data.reset_form_values);
    });
  });
  describe('check modal show functions', () => {
    it('should change set form values to true', () => {
      assert.isFalse(wrapper.vm.$data.set_form_values);
      const bm = wrapper.find(BaseModal);
      bm.vm.$emit('modal_show');
      assert.equal(bm.emitted().modal_show.length, 1);
      assert.isTrue(wrapper.vm.$data.set_form_values);
    });
  });
});
