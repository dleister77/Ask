import form_suggestion from '../src/components/form-suggestion';
import { len } from 'vuelidate/lib/validators/common';

const describe = require('mocha').describe;
const it = require('mocha').it;
const assert = require('chai').assert
const sinon = require('sinon');

const App = Vue.component('app', form_suggestion);

const get_sector_list_stub = sinon.stub().returns([
    {id: 1, name: "test sector 1"},
    {id: 2, name: "test sector 2"}
]);

const get_category_list_stub = sinon.stub()
get_category_list_stub.withArgs().returns([
    {id: 1, name: "test category 1"},
    {id: 2, name: "test category 2"},
    {id: 3, name: "test category 3"}
]);
get_category_list_stub.withArgs(1).returns([
    {id: 1, name: "test category 1"},
]);
get_category_list_stub.withArgs(2).returns([
    {id: 2, name: "test category 2"},
    {id: 3, name: "test category 3"}
]);

let mountOptions = {
    propsData: {
        form_presets: {
            csrf_token: 'test_csrf_token',
            id: "1",
            name: "Doug's Testing Center",
            // is_not_active: false,
            // category_updated: false,
            sector: 1,
            category: [1],
            address_updated: false,
            address: {
                line1: "1000 Test St",
                line2: "",
                city: "Charlotte",
                state: 28,
                zip: "28210",
                // coordinate_error: false,
            },
            // contact_info_updated: false,
            email: "test@test.com",
            website: "www.testwebsite.com",
            telephone: "1234567890",
        },
        url: "localhost:5000/provider/suggestion",
        reset_form_values: false,
        set_form_values: false,
        submit_form: false,
    },
    methods: {
        get_sector_list: get_sector_list_stub,
        get_category_list: get_category_list_stub,
    },
};



describe('Form Message Suggestion', function(){
    let wrapper;
    beforeEach(async function() {
        wrapper=VueTestUtils.mount(App, mountOptions);
        wrapper.setProps({set_form_values: true});
        await Vue.nextTick();
    });
    afterEach(async function(){
        wrapper.destroy();
        wrapper.setProps({reset_form_values: true})
        await Vue.nextTick();
    });
    describe('check instance', function(){
        it('check that message modal is a vue instance', function(){
        assert.isTrue(wrapper.isVueInstance());
        });
    });
    describe('check initial data values', function() {
        beforeEach(async function() {

        });
        afterEach(async function() {

        })
        it('sector is correct', async function() {
            assert.isTrue(wrapper.vm.$data.options.sectors.length == 2, 'list incorrect');
            assert.equal(wrapper.vm.$data.form.sector, 1, 'selected sector incorrect');
        })
        it('category is correct', function() {
            assert.equal(wrapper.vm.$data.options.categories.length, 1, 'list incorrect');
            assert.equal(wrapper.vm.$data.form.category, 1, 'selected category incorrect')
        })
    })
    describe('check initial rendered fields', function() {
        it('checkbox fields should be rendered', function(){
            assert.isTrue(wrapper.contains("#is_not_active"));
            assert.isTrue(wrapper.contains("#address_updated"));
            assert.isTrue(wrapper.contains("#contact_info_updated"));
            assert.isTrue(wrapper.contains("#category_updated"));
        });
        it('detailed fields should not be rendered', function() {
            assert.isFalse(wrapper.contains('#sector'));
            assert.isFalse(wrapper.contains("#line1"));
            assert.isFalse(wrapper.contains('#website'));
        })

    })
    describe('response to checkbox fields being checked', function() {
        it('address details should display after address_updated checked', async function() {
            let checkfield = wrapper.find('#address_updated');
            checkfield.setChecked();
            await Vue.nextTick();
            assert.isTrue(wrapper.contains('#line1'));
            assert.isTrue(wrapper.contains('#line2'));
            assert.isTrue(wrapper.contains('#city'));
            assert.isTrue(wrapper.contains('#state'));
            assert.isTrue(wrapper.contains('#zip'));
        })
        it('category fields displayed after category_updated checked', async function() {
            let checkfield = wrapper.find('#category_updated');
            checkfield.setChecked();
            await Vue.nextTick();
            assert.isTrue(wrapper.contains('#category'));
            assert.isTrue(wrapper.contains('#sector'));
        })
    })
    describe('responsiveness to sector being changed', function(){       
        it('category options should update after sector changed', async function() {
            await Vue.nextTick();
            assert.equal(wrapper.vm.options.categories.length, 1);
            wrapper.setData({
                form: {
                    sector: 2,
                },
            });
            await Vue.nextTick();
            assert.equal(wrapper.vm.options.categories.length,2);
        })
    })
    describe('form resets properly', function(){
        beforeEach(async function() {
            wrapper.setProps({set_form_values: true});
            await Vue.nextTick();
        });
        afterEach(async function() {
            wrapper.setProps({reset_form_values: true})
            await Vue.nextTick();
        })
        it('should clear form data', async function() {
            wrapper.setProps({reset_form_values: true});
            await Vue.nextTick();
            let vals = Object.values(wrapper.vm.$data.form);
            let length = vals.length;
            let num_reset_vals = vals.reduce(function(accum, curr){
                if (curr == "" || curr == false){
                    accum = accum + 1;
                } else if (typeof curr == 'object' && (len(Object.values(curr)) == len(Object.values(curr).filter((val)=> val=="")))){
                    accum = accum + 1;
                }
                return accum;
            },0);
            assert.equal(length, num_reset_vals);
        })
        it('should reset displayed form validity', async function(){
            wrapper.vm.$v.$touch();
            await Vue.nextTick();
            assert.isTrue(wrapper.vm.$v.$dirty);
            wrapper.setProps({reset_form_values: true});
            await Vue.nextTick();
            assert.isFalse(wrapper.vm.$v.$dirty);
        })
    })
    describe('form validity', function(){
        it('should initially be valid', function(){
            assert.isFalse(wrapper.vm.$v.$invalid);
        })
        it('should be invalid after removing required field', async function(){
            assert.isFalse(wrapper.vm.$v.$invalid, "not valid at start of test")
            assert.equal(wrapper.vm.$data.form.address.line1, "1000 Test St", "initial line1 value incorrect")
            let checkfield = wrapper.find('#address_updated');
            checkfield.setChecked();
            await Vue.nextTick();
            assert.isFalse(wrapper.vm.$v.form.address.line1.$invalid, "not valid after address update checked")
            wrapper.setData({form: {address: {line1: ''}}});
            await Vue.nextTick();
            assert.equal(wrapper.vm.$data.form.address.line1, '', 'line1 test update not working');
            assert.isTrue(wrapper.vm.$v.form.address.line1.$invalid, 'line1');
            assert.isFalse(wrapper.vm.$v.form.address.city.$invalid, "city")
            assert.isFalse(wrapper.vm.$v.form.address.state.$invalid, "state")
            assert.isFalse(wrapper.vm.$v.form.address.zip.$invalid, "zip")
            assert.isFalse(wrapper.vm.$v.form.address.coordinate_error.$invalid, "coordinate")






        })
    })
});