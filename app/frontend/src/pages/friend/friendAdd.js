import Vue from 'vue';
import TypeaheadMixin from '../../components/forms/typeahead_mixin';


const friendAdd = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  mixins: [TypeaheadMixin],
  data: {
    urls: links,
    typeahead: {
      include_id: true,
    },
  },
  methods: {
    suggestionSerializer(person) {
      return `${person.first_name} ${person.last_name}, ${person.city} ${person.state}`;
    },
  },
});

export default friendAdd;
