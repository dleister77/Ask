require('jsdom-global')();


const describe = require('mocha').describe;
const it = require('mocha').it;
const beforeEach = require('mocha').beforeEach;
const afterEach = require('mocha').afterEach;
const assert = require('chai').assert
const mocha = require('mocha');
const Vue = require('vue/dist/vue.js');
const VueTestUtils = require('@vue/test-utils');

const App = Vue.component('app', {
    props: {
        showbutton:{
          required: false,
          type: Boolean,
        }
    },
    template: `
    <div>
      <myButton id="b1" v-if="showbutton" ref="mybutton1">button1</myButton>
      <myButton id="b2" v-if="!showbutton" ref="mybutton2">button2</myButton>
    </div>  
    `
  })

  const myButton = Vue.component('myButton', {
      template:`
      <div>
        <button class="button" type="button><slot></slot></button>
      </div>
      `
  });
  
let wrapper;

describe('myTest', function(){
  beforeEach(function(){
    console.log("general setup");
  });
  describe('specific test to run', function(){
    beforeEach(function(){
      console.log('specific setup');
    });
    console.log('now the test');
    it('now the test', function(){
      assert.isTrue(true);
    })
  })
})