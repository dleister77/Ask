import Vue from 'vue';
import { VMoney } from 'v-money';




const review = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  directives: {
    money: VMoney,
  },
  data: {
    form: {
      price_paid: '$ ',
    },
    money: {
      decimal: '.',
      thousands: ',',
      prefix: '$ ',
      suffix: '',
      precision: 0,
      masked: false,
      allowBlank: true,
      min: 1,
    },
  },
  computed: {
    show_money() {
      return !(this.form.price_paid == '$ ' || this.form.price_paid === '$ 0');
    },
  },
  methods: {
    setRequired() {
      const radioChoices = document.querySelectorAll("input[type='radio']");
      radioChoices.forEach((element) => element.setAttribute('required', true));
    },
  },
  mounted() {
    this.setRequired();
  },
  watch: {
    'form.price_paid': function(new_val) {
      if (new_val === '$ 0') {
        this.form.price_paid = '$ ';
      }
    },
  },
});

export default review;
