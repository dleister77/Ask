
import {reset_form, set_form} from '../src/scripts/forms';

const describe = require('mocha').describe;
const it = require('mocha').it;
const assert = require('chai').assert
const sinon = require('sinon');



describe('form_reset', function() {
    it('reset form values', function() {
        let test_case = {
            id: 1,
            name: "Doug",
            dogs: ["porter", "salty", "wendy"],
            is_old: true,
        };
        let new_form = reset_form(test_case);
        assert.equal(new_form.id, 0, "number fails");
        assert.equal(new_form.name, "", "string fails");
        assert.equal(JSON.stringify(new_form.dogs), JSON.stringify([]), "array fails");
        assert.equal(new_form.is_old, false, 'boolean fails');
    })
    it('reset form values nested object', function() {
        let test_case = {
            id: 1,
            name: "Doug",
            dog: {name: "porter", age: 6, is_grumpy:  true},
            is_old: true,
        };
        let new_form = reset_form(test_case);
        assert.equal(new_form.id, 0, "number fails");
        assert.equal(new_form.name, "", "string fails");
        assert.equal(JSON.stringify(new_form.dog), JSON.stringify({name: "", age: 0, is_grumpy: false}), "object literal fails");
        assert.equal(new_form.is_old, false, 'boolean fails');
    })
})

describe('set_form', function() {
    it('sets non nested form values', function() {
        let form_presets = {
            id: 1,
            name: "Doug",
        }
        let form = {
            id: "",
            name: ""
        }
        form = set_form(form_presets, form);
        assert.equal(form.id, 1);
        assert.equal(form.name, "Doug");
    })
    it('sets non nested form values with additional fields in target', function() {
        let form_presets = {
            id: 1,
            name: "Doug",
            categories: ["dog", "cat"]
        }
        let form = {
            id: "",
            name: "",
            categories: [],
            check: false,
        }
        form = set_form(form_presets, form);
        assert.equal(form.id, 1);
        assert.equal(form.name, "Doug");
        assert.equal(form.check, false), "non preset fails";
        assert.equal(JSON.stringify(form.categories), JSON.stringify(form_presets.categories), "array fails")
    })

    it('sets nested form values', function() {
        let form_presets = {
            id: 1,
            name: "Doug",
            pet: {name: "porter", type: "dog", age: 6}
        }
        let form = {
            id: "",
            name: "",
            pet: {name: "", type: "", age: 0},
        }
        form = set_form(form_presets, form);
        assert.equal(form.id, 1);
        assert.equal(form.name, "Doug");
        assert.equal(JSON.stringify(form.pet), JSON.stringify(form_presets.pet), "nested object fails")
    })
    it('sets nested form values with additional fields in form', function() {
        let form_presets = {
            id: 1,
            name: "Doug",
            pet: {name: "porter", type: "dog", age: 6}
        }
        let form = {
            id: "",
            name: "",
            pet: {name: "", type: "", age: 0, has_hair: true},
        }
        form = set_form(form_presets, form);
        assert.equal(form.pet.name, "porter", 'common nested fields fail')
        assert.equal(form.pet.has_hair, true, 'additional nested form fields fail');
    })

})
