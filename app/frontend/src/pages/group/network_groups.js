import Vue from 'vue';
import TypeaheadMixin from '../../components/forms/typeahead_mixin';


const groupAdd = new Vue({
  el: '#appContent',
  delimiters: ['[[', ']]'],
  mixins: [TypeaheadMixin],
  data: {
    typeahead: {
      include_id: false,
    },
    urls: links,
  },
});

export default groupAdd;
