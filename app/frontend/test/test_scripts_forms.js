
import { resetForm, setForm } from '../src/scripts/forms';

const describe = require('mocha').describe;
const it = require('mocha').it;
const assert = require('chai').assert
const sinon = require('sinon');


describe('form_reset', () => {
  it('reset form values', () => {
    const testCase = {
      id: 1,
      name: 'Doug',
      dogs: ['porter', 'salty', 'wendy'],
      is_old: true,
    };
    const newForm = resetForm(testCase);
    assert.equal(newForm.id, 0, 'number fails');
    assert.equal(newForm.name, '', 'string fails');
    assert.equal(JSON.stringify(newForm.dogs), JSON.stringify([]), 'array fails');
    assert.equal(newForm.is_old, false, 'boolean fails');
  });
  it('reset form values nested object', () => {
    const testCase = {
      id: 1,
      name: 'Doug',
      dog: { name: 'porter', age: 6, is_grumpy: true },
      is_old: true,
    };
    const newForm = resetForm(testCase);
    assert.equal(newForm.id, 0, 'number fails');
    assert.equal(newForm.name, '', 'string fails');
    assert.equal(
      JSON.stringify(newForm.dog),
      JSON.stringify({ name: '', age: 0, is_grumpy: false }),
      'object literal fails'
    );
    assert.equal(newForm.is_old, false, 'boolean fails');
  });
});

describe('set_form', () => {
  it('sets non nested form values', () => {
    const formPresets = {
      id: 1,
      name: 'Doug',
    };
    let form = {
      id: '',
      name: '',
    };
    form = setForm(formPresets, form);
    assert.equal(form.id, 1);
    assert.equal(form.name, 'Doug');
  });
  it('sets non nested form values with additional fields in target', () => {
    const formPresets = {
      id: 1,
      name: 'Doug',
      categories: ['dog', 'cat'],
    };
    let form = {
      id: '',
      name: '',
      categories: [],
      check: false,
    };
    form = setForm(formPresets, form);
    assert.equal(form.id, 1);
    assert.equal(form.name, 'Doug');
    assert.equal(form.check, false, 'non preset fails');
    assert.equal(JSON.stringify(form.categories), JSON.stringify(formPresets.categories), 'array fails');
  });

  it('sets nested form values', () => {
    const formPresets = {
      id: 1,
      name: 'Doug',
      pet: { name: 'porter', type: 'dog', age: 6 }
    };
    let form = {
      id: '',
      name: '',
      pet: { name: '', type: '', age: 0 },
    };
    form = setForm(formPresets, form);
    assert.equal(form.id, 1);
    assert.equal(form.name, 'Doug');
    assert.equal(JSON.stringify(form.pet), JSON.stringify(formPresets.pet), 'nested object fails');
  });
  it('sets nested form values with additional fields in form', () => {
    const formPresets = {
      id: 1,
      name: 'Doug',
      pet: { name: 'porter', type: 'dog', age: 6 },
    };
    let form = {
      id: '',
      name: '',
      pet: {
        name: '',
        type: '',
        age: 0,
        has_hair: true,
      },
    };
    form = setForm(formPresets, form);
    assert.equal(form.pet.name, 'porter', 'common nested fields fail');
    assert.equal(form.pet.has_hair, true, 'additional nested form fields fail');
  });
});
