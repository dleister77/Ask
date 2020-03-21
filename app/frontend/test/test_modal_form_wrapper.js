
import modal_form_wrapper from '../src/components/modal-form-wrapper';
import base_modal from '../src/components/base-modal'

const describe = require('mocha').describe;
const it = require('mocha').it;
const assert = require('chai').assert
const sinon = require('sinon');

const App = Vue.component('app', modal_form_wrapper);

require('bootstrap');


let mountOptions = {
    propsData: {
        title: "test-modal",
        url: "localhost:5000/test",
    },
};


describe('modal form wrapper', function() {
    let wrapper;
    beforeEach(function() {
        wrapper=VueTestUtils.mount(App, mountOptions);
    })
    afterEach(function() {
        wrapper.destroy();
    })
    describe('check instance', function(){
        it('check that message modal is a vue instance', function(){
        assert.isTrue(wrapper.isVueInstance());
        });
    });
    describe('check modal hide functions', function() {
        it('should change reset form values to true', function() {
            assert.isFalse(wrapper.vm.reset_form_values);
            let bm = wrapper.find(base_modal);
            bm.vm.$emit('modal_hide');
            assert.equal(bm.emitted().modal_hide.length, 1);
            assert.isTrue(wrapper.vm.$data.reset_form_values);
        });
    });
    describe('check modal show functions', function() {
        it('should change set form values to true', function() {
            assert.isFalse(wrapper.vm.$data.set_form_values);
            let bm = wrapper.find(base_modal);
            bm.vm.$emit('modal_show');
            assert.equal(bm.emitted().modal_show.length, 1);
            assert.isTrue(wrapper.vm.$data.set_form_values);
        })
    })
})
