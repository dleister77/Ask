import FormRegister from '../src/components/form-register';

const { afterEach, beforeEach, describe, it } = require('mocha');
const { assert } = require('chai');
const sinon = require('sinon');


const App = Vue.component('app', FormRegister);

const mountOptions = {
  propsData: {
    form_presets: {
      first_name: '',
      last_name: '',
      address: {
        line1: '',
        line2: '',
        city: '',
        state: 0,
        zip: '',
      },
      email: '',
      username: '',
      password: '',
      confirmation: '',
    },
    server_side_errors: {
      first_name: [],
      last_name: [],
      address: {
        line1: [],
        line2: [],
        city: [],
        state: [],
        zip: [],
      },
      email: [],
      username: [],
      password: [],
      confirmation: [],
    },
    url: 'localhost:5000/message/send',
    reset_form_values: false,
    set_form_values: true,
    submit_form: false,
    form_errors: {},
  },
  methods: {},
  delimiters: ['[[', ']]'],
};

const validFormEntries = {
  first_name: 'Barry',
  last_name: 'Obama',
  address: {
    line1: '10 Main St',
    line2: '',
    city: 'Chicago',
    state: 12,
    zip: '20000',
  },
  email: 'bobama@pres.gov',
  username: 'bobama',
  password: 'password5',
  confirmation: 'password5',
};

describe('Form Message Suggestion', () => {
  let wrapper;
  beforeEach(async () => {
    wrapper = VueTestUtils.mount(App, mountOptions);
  });
  afterEach(async () => {
    wrapper.destroy();
  });
  describe('check instance', () => {
    it('check that message modal is a vue instance', () => {
      assert.isTrue(wrapper.isVueInstance());
    });
  });
  describe('check initial validity', () => {
    beforeEach(async () => {
      wrapper.vm.$v.$reset();
    });
    it('should be invalid, but display no errors', () => {
      assert.isTrue(wrapper.vm.$v.$invalid);
      assert.isFalse(wrapper.vm.$v.$error);
      const errors = wrapper.findAll('.form-error-message');
      assert.equal(errors.length, 0);
    });
    it('should show errors after fields touched', async () => {
      wrapper.vm.$v.$touch();
      await Vue.nextTick();
      assert.isTrue(wrapper.vm.$v.$error);
      const errors = wrapper.findAll('.form-error-message');
      assert.equal(errors.length, 10);
      const errorMessages = errors.wrappers.map((error) => error.text());
      assert.isTrue(errorMessages.includes('First Name is required.'))
    });
  });
  describe('validity after entering invalid values', () => {
    beforeEach(() => wrapper.vm.$v.$reset());
    it('should show an error with none 5 digit zip', async () => {
      wrapper.setData({ form: { address: { zip: '123' } } });
      const zip = wrapper.find({ ref: 'address-zip' });
      zip.props().validator.$touch();
      await Vue.nextTick();
      const error = zip.find('.form-error-message');
      assert.equal(error.text(), 'Zip code must be 5 characters in length.');
    });
    it('should show error for bad email address', async () => {
      wrapper.setData({ form: { email: 'lbgooglecom' } });
      const email = wrapper.find({ ref: 'email' });
      email.props().validator.$touch();
      await Vue.nextTick();
      const error = email.find('.form-error-message');
      assert.equal(error.text(), 'Invalid email address.');
    });
    it('should throw an error when password too short', async () => {
      wrapper.setData({ form: { password: 'test' } });
      const password = wrapper.find({ ref: 'password' });
      password.props().validator.$touch();
      await Vue.nextTick();
      const error = password.find('.form-error-message');
      assert.equal(error.text(), 'Password must be between 7 & 15 characters in length.');
    });
    it('should throw an error when password too long', async () => {
      wrapper.setData({ form: { password: 'testtesttesttest' } });
      const password = wrapper.find({ ref: 'password' });
      password.props().validator.$touch();
      await Vue.nextTick();
      const error = password.find('.form-error-message');
      assert.equal(error.text(), 'Password must be between 7 & 15 characters in length.');
    });
    it('should throw an error when password and confirmation do not match', async () => {
      const testForm = {
        password: 'password1',
        confirmation: 'password3',
      };
      wrapper.setData({ form: testForm });
      const password = wrapper.find({ ref: 'password' });
      password.props().validator.$touch();
      const confirmation = wrapper.find({ ref: 'confirmation' });
      confirmation.props().validator.$touch();
      await Vue.nextTick();
      const error = confirmation.find('.form-error-message');
      assert.equal(error.text(), 'Confirmation does not match entered password.');
    });
  });
  describe('check rendered server side errors', () => {
    beforeEach(async () => {
      const testCase = {
        first_name: ['incorrect name'],
        address: {
          city: ['incorrect city'],
          state: ['incorrect state'],
        },
      };
      wrapper.vm.$v.$reset();
      wrapper.setData({ server_side_errors: testCase });
      await Vue.nextTick();
      assert.equal(JSON.stringify(wrapper.vm.server_side_errors.first_name), JSON.stringify(['incorrect name']), 'sse data not being set correctly');
    });
    it('generates correct number of errors', () => {
      const errors = wrapper.findAll('.form-error-message');
      assert.equal(errors.length, 3);
    });
    it('should render desired error messages', () => {
      const firstName = wrapper.find({ ref: 'first_name' });
      const sse = firstName.find('.form-error-message');
      assert.equal(sse.text(), 'incorrect name');
    });
  });
  describe('check submit', () => {
    beforeEach(async () => {
      wrapper.setData({ form: validFormEntries });
      await Vue.nextTick();
    });
    it('set form to valid values', () => {
      assert.isFalse(wrapper.vm.$v.$invalid);
    });
    it('should call submit', () => {
      const sandbox = sinon.createSandbox();
      sandbox.stub(HTMLFormElement, 'submit').value(true);



    });
  });
});
