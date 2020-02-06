import message_read from '../app/static/components/message-read';

require('jsdom-global')();
const describe = require('mocha').describe;
const it = require('mocha').it;
const beforeEach = require('mocha').beforeEach;
const afterEach = require('mocha').afterEach;
const assert = require('chai').assert

const Vue = require('vue/dist/vue.js');
const VueTestUtils = require('@vue/test-utils');

const App = Vue.component('app', message_read);



let mountOptions = {
    propsData: {
        message: {
            sender_full_name: "test_sender",
            timestamp: new Date(Date.UTC(2020, 0, 28, 10, 0, 0)),
            subject: "test_subject",
            body: "test_body"
        }
    }
};



describe('displayed message', function(){
    let wrapper;
    before( async function(){
        wrapper = VueTestUtils.mount(App, mountOptions);
    });
    after(function(){
        wrapper.destroy();
    })
    it('check set up', function(){
        assert.isTrue(wrapper.isVueInstance());
    });
    it('should have sender_name', function(){
        assert.isTrue(wrapper.text().includes("test_sender"));
    });
    it('should have subject', function(){
        assert.isTrue(wrapper.text().includes("test_subject"));
    })
    it('should have body', function(){
        assert.isTrue(wrapper.text().includes("test_body"));
    })
    it('should render timestamp correctly', function(){
        assert.isTrue(wrapper.text().includes("January 28, 2020 at 5:00 AM"))
    })
});