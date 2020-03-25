import Vue from 'vue';
import { categoryGet } from '../../scripts/forms';


const providerAdd = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    form: {
      name: '',
      sector: 1,
      category: [],
      email: '',
      website: '',
      telephone: '',
      addressUnknown: false,
      line1: '',
      line2: '',
      city: '',
      zip: '',
      state: '',
    },
    show: {
      partial_address: false,
    },
    urls: links,
  },
  methods: {
    updateCategory() {
      categoryGet(this.urls.categoryList, this.form.sector, 'category');
      this.form.category = [];
    },
  },
  mounted() {
    const select = document.getElementById('category');
    this.form.category.push(select.firstElementChild.value);
  },
  watch: {
    'form.addressUnknown': function () {
      this.show.partial_address = !this.show.partial_address;
    },
  },
});

export default providerAdd;
