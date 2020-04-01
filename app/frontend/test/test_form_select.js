import FormSelect from '../src/components/forms/form-input-select';

const { describe, it, beforeEach } = require('mocha');
const { assert } = require('chai');

const App = Vue.component('app', FormSelect);


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
    value: 1,
    validator: validRequiredStub,
    options: [
      {
        id: 1,
        name: 'test value 1',
      },
      {
        id: 2,
        name: 'test value 2',
      },
    ],
  },
  methods: {},
  delimiters: ['[[', ']]'],
};


describe('Form Select Group', () => {
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
      assert.equal(wrapper.props().value, 1);
      assert.equal(wrapper.props().options.length, 2);
      const options = wrapper.findAll('option');
      assert.equal(options.length, 3);
      const select = wrapper.find('select').element;
      assert.equal(select.value, 1);
      assert.isFalse(wrapper.props().validator.$error);
    });
    it('does not render error messages when valid', () => {
      const errors = wrapper.findAll('.form-error-message');
      assert.equal(errors.length, 0);
    });
  });
  describe('check change input', () => {
    beforeEach(async () => {
      const select = wrapper.find('select');
      const options = select.findAll('option');
      options.at(2).setSelected();
      await Vue.nextTick();
    });
    it('option should be selected', () => {
      assert.isTrue(wrapper.findAll('option').at(2).element.selected);
    });
    it('select value should be updated', () => {
      assert.equal(wrapper.find('select').element.value, 2);
    });
  });
  describe('only adds 0 index option if needed', () => {
    beforeEach(async () => {
      wrapper.setProps(
        {
          options:
          [
            {
              id: 0,
              name: 'not needed',
            },
            {
              id: 1,
              name: 'test value',
            },
          ],
        },
      );
      await Vue.nextTick();
    });
    it('recognizes supplied options start at 0', () => {
      assert.isTrue(wrapper.vm.options_start_at_0);
    });
    it('should only render 2 options', () => {
      const options = wrapper.findAll('option');
      assert.equal(options.length, 2);
    });
  });
});
