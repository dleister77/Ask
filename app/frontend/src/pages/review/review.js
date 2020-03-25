import Vue from 'vue';


const review = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {},
  methods: {
    setRequired() {
      const radioChoices = document.querySelectorAll("input[type='radio']");
      radioChoices.forEach((element) => element.setAttribute('required', true));
    },
  },
  mounted() {
    this.setRequired();
  },
});

export default review;
