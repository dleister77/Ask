import axios from 'axios';

import FormUsermessage from '../src/components/form-usermessage';

const { after, afterEach, before, beforeEach, describe, it } = require('mocha');
const { assert } = require('chai');
const sinon = require('sinon');

const App = Vue.component('app', FormUsermessage);

const mountOptions = {
  propsData: {
    form_presets: {
      csrf: 'testscrsf',
      recipient_id: 1,
      recipient_name: 'test_name',
      subject: 'test_subject',
    },
    url: 'localhost:5000/message/send',
    reset_form_values: false,
    set_form_values: false,
    submit_form: false,
  },
  methods: {},
};


describe('Form Message Suggestion', () => {
  let wrapper;
  beforeEach(async () => {
    wrapper = VueTestUtils.mount(App, mountOptions);
    wrapper.setProps({ set_form_values: true });
    await Vue.nextTick();
  });
  afterEach(async () => {
    wrapper.destroy();
    wrapper.setProps({ reset_form_values: true });
    await Vue.nextTick();
  });
  describe('check instance', () => {
    it('check that message modal is a vue instance', () => {
      assert.isTrue(wrapper.isVueInstance());
    });
  });

  describe('check initial', () => {
    it('data_values', async () => {
      assert.equal(wrapper.vm.form.recipient_id, mountOptions.propsData.form_presets.recipient_id);
      assert.equal(
        wrapper.vm.form.recipient_name,
        mountOptions.propsData.form_presets.recipient_name,
      );
    });
    it('renders correctly', () => {
      const name = wrapper.find('#recipient');
      assert.equal(name.element.value, mountOptions.propsData.form_presets.recipient_name);
    });
    it('is initially invalid', () => {
      assert.isTrue(wrapper.vm.$v.$invalid);
      assert.isFalse(wrapper.vm.$v.$error);
    });
  });

  describe('check renders invalid after dirty', () => {
    beforeEach(async () => {
      wrapper.vm.$v.$touch();
      await Vue.nextTick();
    });
    afterEach(async () => {
      wrapper.vm.$v.$reset();
      await Vue.nextTick();
    });
    it('should now be invalid and dirty', () => {
      assert.isTrue(wrapper.vm.$v.$error);
    });
    it('should now include 1 error message', () => {
      const errors = wrapper.findAll('.form-error-message');
      assert.equal(errors.length, 1, 'incorrect number of error messages rendered');
    });
    it('should render correct text in error message', () => {
      const error = wrapper.find('.form-error-message');
      assert.equal(error.text(), 'Message body is required.');
    });
  });

  describe('check required validators when fields set to blank', () => {
    beforeEach(async () => {
      const badForm = {
        recipient_id: '',
        recipient_name: '',
        subject: '',
        body: '',
      };
      wrapper.setData({ form: badForm });
      wrapper.vm.$v.$touch();
      await Vue.nextTick();
    });
    afterEach(async () => {
      const originalForm = mountOptions.propsData.form_presets;
      wrapper.setData({ form: originalForm });
      wrapper.vm.$v.$reset();
      await Vue.nextTick();
    });
    describe('check validators', () => {
      it('should be be invalid', () => {
        assert.isTrue(wrapper.vm.$v.form.$invalid);
      });
    });
    describe('check rendered error messages', () => {
      let message;
      it('name required should be displayed', () => {
        message = wrapper.find({ ref: 'recipient' }).find('.form-error-message');
        assert.isFalse(message.isEmpty());
        assert.equal(message.text(), 'To is required.');
      });
      it('subject required should be displayed', () => {
        message = wrapper.find({ ref: 'subject' }).find('.form-error-message');
        assert.isFalse(message.isEmpty());
        assert.equal(message.text(), 'Subject is required.');
      });
      it('message body required should be displayed', () => {
        message = wrapper.find({ ref: 'body' }).find('.form-error-message');
        assert.isFalse(message.isEmpty());
        assert.equal(message.text(), 'Message body is required.');
      });
    });
  });

  describe('check submit', () => {
    let stubPost;
    let stubAlert;
    beforeEach(async () => {
      stubPost = sinon.stub(axios, 'post').resolves({ status: 200, data: { status: 'success' } });
      stubAlert = sinon.stub(global, 'alert').callsFake((msg) => console.log(msg));
      wrapper.setData({ form: { body: 'test body' } });
      await Vue.nextTick();
    });
    afterEach(() => {
      stubPost.restore();
      stubAlert.restore();
    });
    it('verify form is valid', () => {
      assert.isTrue(wrapper.vm.form.body === 'test body');
      assert.isFalse(wrapper.vm.$v.$invalid);
    });
    it('should send and reset form values', async () => {
      const button = wrapper.find('button');
      await button.trigger('click');
      assert.equal(wrapper.vm.form.subject, '');
    });
  });
});
