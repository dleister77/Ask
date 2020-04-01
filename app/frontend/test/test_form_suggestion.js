import FormSuggestion from '../src/components/form-suggestion';

const { describe, it } = require('mocha');
const { assert } = require('chai');
const sinon = require('sinon');

const App = Vue.component('app', FormSuggestion);

const getSectorListStub = sinon.stub().returns([
  { id: 1, name: 'test sector 1' },
  { id: 2, name: 'test sector 2' },
]);

const getCategoryListStub = sinon.stub();
getCategoryListStub.withArgs().returns([
  { id: 1, name: 'test category 1' },
  { id: 2, name: 'test category 2' },
  { id: 3, name: 'test category 3' },
]);
getCategoryListStub.withArgs(1).returns([
  { id: 1, name: 'test category 1' },
]);
getCategoryListStub.withArgs(2).returns([
  { id: 2, name: 'test category 2' },
  { id: 3, name: 'test category 3' },
]);

const mountOptions = {
  propsData: {
    form_presets: {
      csrf_token: 'test_csrf_token',
      id: '1',
      name: "Doug's Testing Center",
      sector: 1,
      category: [1],
      address_updated: false,
      address: {
        line1: '1000 Test St',
        line2: '',
        city: 'Charlotte',
        state: 28,
        zip: '28210',
      },
      email: 'test@test.com',
      website: 'www.testwebsite.com',
      telephone: '1234567890',
    },
    url: 'localhost:5000/provider/suggestion',
    reset_form_values: false,
    set_form_values: false,
    submit_form: false,
  },
  methods: {
    get_sector_list: getSectorListStub,
    get_category_list: getCategoryListStub,
  },
};

function determineType(val) {
  if (typeof val === 'string') {
    return 'string';
  }
  if (typeof val === 'number') {
    return 'number';
  } if (typeof val === 'boolean') {
    return 'boolean';
  } if (val instanceof Array) {
    return 'array';
  } return 'object';
}

function checkResetValue(val) {
  const isAllowedPrimitive = ['', 0, false].includes(val);
  switch (determineType(val)) {
    case 'array': {
      const valString = JSON.stringify(val);
      const checkString = JSON.stringify([]);
      return valString === checkString;
    }
    case 'object': {
      const isResetObject = !Object.values(val).map(checkResetValue).includes(false);
      return isResetObject;
    }
    default:
      return isAllowedPrimitive;
  }
}

describe('Form Message Suggestion', () => {
  let wrapper;
  beforeEach(async () => {
    wrapper=VueTestUtils.mount(App, mountOptions);
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
  describe('check initial data values', () => {
    it('sector is correct', async () => {
      assert.isTrue(wrapper.vm.$data.options.sectors.length === 2, 'list incorrect');
      assert.equal(wrapper.vm.$data.form.sector, 1, 'selected sector incorrect');
    });
    it('category is correct', () => {
      assert.equal(wrapper.vm.$data.options.categories.length, 1, 'list incorrect');
      assert.equal(wrapper.vm.$data.form.category, 1, 'selected category incorrect');
    });
  });
  describe('check initial rendered fields', () => {
    it('checkbox fields should be rendered', () => {
      assert.isTrue(wrapper.contains('#is_not_active'));
      assert.isTrue(wrapper.contains('#address_updated'));
      assert.isTrue(wrapper.contains('#contact_info_updated'));
      assert.isTrue(wrapper.contains('#category_updated'));
    });
    it('detailed fields should not be rendered', () => {
      assert.isFalse(wrapper.contains('#sector'));
      assert.isFalse(wrapper.contains('#category'));
      assert.isFalse(wrapper.contains('#line1'));
      assert.isFalse(wrapper.contains('#line2'));
      assert.isFalse(wrapper.contains('#city'));
      assert.isFalse(wrapper.contains('#state'));
      assert.isFalse(wrapper.contains('#zip'));
      assert.isFalse(wrapper.contains('#coordinate_error'));
      assert.isFalse(wrapper.contains('#website'));
      assert.isFalse(wrapper.contains('#telephone'));
      assert.isFalse(wrapper.contains('#email'));
    });
  });
  describe('response to checkbox fields being checked', () => {
    it('address details should display after address_updated checked', async () => {
      const checkField = wrapper.find('#address_updated');
      checkField.setChecked();
      await Vue.nextTick();
      assert.isTrue(wrapper.contains('#line1'));
      assert.isTrue(wrapper.contains('#line2'));
      assert.isTrue(wrapper.contains('#city'));
      assert.isTrue(wrapper.contains('#state'));
      assert.isTrue(wrapper.contains('#zip'));
    });
    it('category fields displayed after category_updated checked', async () => {
      const checkField = wrapper.find('#category_updated');
      checkField.setChecked();
      await Vue.nextTick();
      assert.isTrue(wrapper.contains('#category'));
      assert.isTrue(wrapper.contains('#sector'));
    });
    it('contact fields displayed after contact_info_update checked', async () => {
      const checkField = wrapper.find('#contact_info_updated');
      checkField.setChecked();
      await Vue.nextTick();
      assert.isTrue(wrapper.contains('#telephone'));
      assert.isTrue(wrapper.contains('#email'));
      assert.isTrue(wrapper.contains('#website'));
    });
  });
  describe('responsiveness to sector being changed', () => {
    it('category options should update after sector changed', async () => {
      await Vue.nextTick();
      assert.equal(wrapper.vm.options.categories.length, 1);
      wrapper.setData({
        form: {
          sector: 2,
        },
      });
      await Vue.nextTick();
      assert.equal(wrapper.vm.options.categories.length, 2);
    });
  });
  describe('form resets properly', () => {
    beforeEach(async () => {
      wrapper.setProps({ set_form_values: true });
      await Vue.nextTick();
    });
    afterEach(async () => {
      wrapper.setProps({ reset_form_values: true });
      await Vue.nextTick();
    });
    it('should clear form data', async () => {
      wrapper.setProps({ reset_form_values: true });
      await Vue.nextTick();
      const vals = Object.values(wrapper.vm.$data.form);
      const { length } = vals;
      const numResetVals = vals.reduce((accum, curr, index, array ) => {
        const updatedAccum = checkResetValue(curr) ? Number(accum) + 1 : Number(accum);
        return updatedAccum;
      }, 0);
      assert.equal(length, numResetVals);
    });
    it('should reset displayed form validity', async () => {
      wrapper.vm.$v.$touch();
      await Vue.nextTick();
      assert.isTrue(wrapper.vm.$v.$dirty);
      wrapper.setProps({ reset_form_values: true });
      await Vue.nextTick();
      assert.isFalse(wrapper.vm.$v.$dirty);
    });
  });
  describe('form validity', () => {
    beforeEach(async () => {
      wrapper.vm.$v.$reset();
      await Vue.nextTick();
    });
    it('should initially be valid', () => {
      assert.isFalse(wrapper.vm.$v.$invalid);
    });
    describe('address fields are required when address updated checked', () => {
      it('should be invalid after removing required fields', async () => {
        const checkfield = wrapper.find('#address_updated');
        checkfield.setChecked();
        const testAddress = {
          line1: '',
          line2: '',
          city: '',
          zip: '',
          state: '',
        };
        wrapper.setData({ form: { address: testAddress } });
        wrapper.vm.$v.$touch();
        await Vue.nextTick();
        assert.isTrue(wrapper.vm.$v.$error);
        const errors = wrapper.findAll('.form-error-message');
        assert.equal(errors.length, 4, `incorrect number of errors rendered: ${errors.length}`);
        const errorMessages = errors.wrappers.map((w) => w.text());
        assert.isTrue(errorMessages.includes('Street Address is required.'));
        assert.isTrue(errorMessages.includes('City is required.'));
        assert.isTrue(errorMessages.includes('Zip Code is required.'));
        assert.isTrue(errorMessages.includes('State is required.'));
      });
    });
    describe('category/sector are required when category updated checked', () => {
      it('should be invalid after removing required fields', async () => {
        const checkfield = wrapper.find('#category_updated');
        checkfield.setChecked();
        wrapper.setData({ form: { category: '', sector: '' } });
        wrapper.vm.$v.$touch();
        await Vue.nextTick();
        assert.isTrue(wrapper.vm.$v.$error);
        const errors = wrapper.findAll('.form-error-message');
        assert.equal(errors.length, 2, `incorrect number of errors rendered: ${errors.length}`);
        const errorMessages = errors.wrappers.map((w) => w.text());
        assert.isTrue(errorMessages.includes('Category is required.'));
        assert.isTrue(errorMessages.includes('Sector is required.'));
      });
    });
    describe('contact info are required when contact info updated checked', () => {
      it('should be invalid after removing required fields', async () => {
        const checkfield = wrapper.find('#contact_info_updated');
        checkfield.setChecked();
        wrapper.setData({ form: { telephone: '' } });
        wrapper.vm.$v.$touch();
        await Vue.nextTick();
        assert.isTrue(wrapper.vm.$v.$error);
        const errors = wrapper.findAll('.form-error-message');
        assert.equal(errors.length, 1, `incorrect number of errors rendered: ${errors.length}`);
        const errorMessages = errors.wrappers.map((w) => w.text());
        assert.isTrue(errorMessages.includes('Telephone is required.'));
      });
    });
  });
});
