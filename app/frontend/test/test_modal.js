
import base_modal from '../src/components/base-modal';

const describe = require('mocha').describe;
const it = require('mocha').it;
const assert = require('chai').assert
const sinon = require('sinon');

const App = Vue.component('app', base_modal);

require('bootstrap');


let mountOptions = {
    propsData: {
        modal_id: "test-modal",
        title: "My Test Modal",
        show_modal: false,
        hide_modal: false,
    },
};



describe('modal', function() {
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
    describe('check manual hide and show', function() {
        it('should show when show_modal set to true', async function() {
            wrapper.setProps({show_modal: true});
            assert.equal(wrapper.vm.show_modal, true, 'prop not set')
            await Vue.nextTick();
            assert.equal(wrapper.emitted().modal_show.length, 1, 'show event not emitted');
        })
        it('should hide when hide_modal set to true', async function() {
            wrapper.setProps({hide_modal: true});
            assert.equal(wrapper.vm.hide_modal, true, 'prop not set')
            await Vue.nextTick();
            assert.equal(wrapper.emitted().modal_hide.length, 1, 'hide event not emitted');
        })
    })
    describe('jQuery eventListeners', function() {
        describe('show', function() {
            it('emit modal show', async function() {
                $(wrapper.vm.$refs.vuemodal).modal('show');
                await Vue.nextTick();
                assert.equal(wrapper.emitted().modal_show.length, 1, 'modal show not emitted');
            })
        })
        describe('hide', function() {
            it('emit modal hide', async function() {
                $(wrapper.vm.$refs.vuemodal).modal('hide');
                await Vue.nextTick();
                assert.equal(wrapper.emitted().modal_hide.length, 1, 'modal hide not emitted');
                assert.equal(wrapper.emitted().modal_is_hidden.length, 1, 'modal hidden not emitted');
            })
        })        
    })
})
