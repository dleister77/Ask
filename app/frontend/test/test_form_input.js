import FormInput from '../src/components/forms/form-input';

const { describe, it, before, beforeEach } = require('mocha');
const { assert } = require('chai');

const App = Vue.component('app', FormInput);


const invalidRequiredStub = {
  $error: true,
  required: false,
  $dirty: true,
};

const validRequiredStub = {
  $error: false,
  required: true,
  $dirty: true,
};

const mountOptions = {
  propsData: {
    name: 'name',
    value: 'testing value',
    validator: validRequiredStub,
  },
  methods: {},
};


describe('Form Input Group', () => {
  let wrapper;
  beforeEach(async () => {
    wrapper=VueTestUtils.mount(App, mountOptions);
    await Vue.nextTick();
  });
  afterEach(async () => {
    wrapper.destroy();
    await Vue.nextTick();
  });
  describe('check instance', () => {
    it('check that message modal is a vue instance', () => {
      assert.isTrue(wrapper.isVueInstance());
    });
  });
  describe('check initial data values', () => {
    it('value is correct', async () => {
      assert.equal(wrapper.props().value, 'testing value');
      const inputs = wrapper.findAll('input');
      const input = inputs.at(0);
      assert.equal(input.element.value, 'testing value', 'input field value not being set');
      assert.isFalse(wrapper.props().validator.$error);
    });
    it('does not render error messages when valid', () => {
      const errors = wrapper.findAll('.form-error-message');
      assert.equal(errors.length, 0);
    });
  });
  describe('check change input', () => {
    let input;
    beforeEach(async () => {
      input = wrapper.find('input');
      input.setValue('new value');
      await Vue.nextTick();
    });
    it('input should reflect new value', () => {
      assert.equal(input.element.value, 'new value');
    });
    it('should emit updated value signal', () => {
      assert.isTrue(wrapper.emitted().input);
    });
  });
  describe('when missing required data', () => {
    beforeEach(async () => {
      wrapper.setProps({
        validator: invalidRequiredStub,
        value: '',
        name: 'name',
      });
      await Vue.nextTick();
    });
    describe('check', () => {
      describe('props', () => {
        it('should equal', () => {
          const props = wrapper.props();
          assert.equal(props.validator.$error, true);
          assert.equal(props.value, '');
        });
      });
      describe('render', () => {
        it('should have 1 error field', () => {
          const errors = wrapper.findAll('.form-error-message');
          assert.equal(errors.length, 1, 'incorrect number error fields rendered');
        });
        it('renders error message text', () => {
          const error = wrapper.find('.form-error-message');
          assert.equal(error.text(), 'name is required.');
        });
      });
    });
  });
  describe('server side errors', () => {
    beforeEach(async () => {
      wrapper.setProps({
        server_side_errors: [
          'incorrect test value',
          'another incorrect value',
        ],
      });
      await Vue.nextTick();
    });
    describe('check', () => {
      describe('props', () => {
        it('should equal', () => {
          const props = wrapper.props();
          assert.equal(props.server_side_errors.length, 2);
          assert.equal(props.server_side_errors[0], 'incorrect test value');
        });
      });
      describe('computed values', () => {
        it('has correct computed values', () => {
          assert.isTrue(wrapper.vm.has_sse);
          assert.isTrue(wrapper.vm.is_invalid);
          assert.equal(
            wrapper.vm.filtered_server_side_errors[0],
            wrapper.props().server_side_errors[0],
          );
          assert.equal(
            wrapper.vm.filtered_server_side_errors[1],
            wrapper.props().server_side_errors[1],
          );
        });
      });
      describe('render', () => {
        it('should have 2 error field', () => {
          const errors = wrapper.findAll('.form-error-message');
          assert.equal(errors.length, 2, 'incorrect number error fields rendered');
        });
        it('renders correct error message text', () => {
          const errors = wrapper.findAll('.form-error-message');
          const sseProps = wrapper.props().server_side_errors;
          assert.equal(errors.at(0).text(), sseProps[0]);
        });
      });
    });
  });
});
