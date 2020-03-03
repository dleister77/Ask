import message_form from '../src/components/message-form';

require('jsdom-global')();
const describe = require('mocha').describe;
const it = require('mocha').it;
const beforeEach = require('mocha').beforeEach;
const afterEach = require('mocha').afterEach;
const assert = require('chai').assert

const Vue = require('vue/dist/vue.js');
const VueTestUtils = require('@vue/test-utils');

const App = Vue.component('app', message_form);


let mountOptions = {
    propsData: {
        is_active
    }
};

describe('check instance', function(){
    let wrapper=VueTestUtils.mount(App);
    it('check that its a vue instance', function(){
    assert.isTrue(wrapper.isVueInstance());
    });
    wrapper.destroy();
});

// describe('visible links', function(){
//     let wrapper;
//     let refsToTest = ['folder-list', 'new-message', 'back-button', 'previous-message','next-message','reply-to', 'move-links-delete','move-links-archive'];
//     describe('show set to true', async function(){
//         before( async function(){
//             wrapper = VueTestUtils.mount(App, mountOptions);
//             wrapper.setProps({folderIsVisible: true, messageIsVisible: true, moveLinksVisible: true});
//             await Vue.nextTick();
//         });
//         after(function(){
//             wrapper.destroy();
//         })
//         it('check set up', function(){
//             assert.isTrue(wrapper.vm.$props.folderIsVisible);
//             assert.isTrue(wrapper.vm.$props.messageIsVisible);
//             assert.isTrue(wrapper.vm.$props.moveLinksVisible);
//         });

//         refsToTest.forEach(function(item){
//             it(item, function(){
//                 assert.isTrue(wrapper.find({ref: item}).exists());
//             });
//         });
//     });

//     describe('show set to false', async function(){
//         before( async function(){
//             wrapper = VueTestUtils.mount(App, mountOptions);
//             wrapper.setProps({folderIsVisible: false, messageIsVisible: false, moveLinksVisible: false});
//             await Vue.nextTick();
//         });
//         after(function(){
//             wrapper.destroy();
//         })
//         it('check set up', function(){
//             assert.isNotTrue(wrapper.vm.$props.folderIsVisible);
//             assert.isNotTrue(wrapper.vm.$props.messageIsVisible);
//             assert.isNotTrue(wrapper.vm.$props.moveLinksVisible);
//         });
//         refsToTest.forEach(function(item){
//             it(item, function(){
//                 assert.isNotTrue(wrapper.find({ref: item}).exists());
//             });
//         });
//     });
// });