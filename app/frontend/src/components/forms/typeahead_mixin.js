import VueBootstrapTypeahead from 'VueBootstrapTypeahead';
import debounce from 'lodash-es/debounce';

const TypeaheadMixin = {
  components: {
    'vue-bootstrap-typeahead': VueBootstrapTypeahead,
  },
  data() {
    return {
      form: {
        id: '',
        name: '',
      },
      typeahead: {
        suggestions: [],
        selected: null,
        include_id: true,
        name_field: 'name',
        id_field: 'id',
      },
      urls: links,
    };
  },
  methods: {
    makeQueryUrl() {
      const input = this.form[this.typeahead.name_field];
      return `${this.urls.autocomplete}?name=${encodeURIComponent(input)}`;
    },
    async getSuggestions() {
      const res = await fetch(this.makeQueryUrl());
      const suggestions = await res.json();
      this.typeahead.suggestions = suggestions;
    },
    suggestionSerializer(item) {
      return `${item.name}`;
    },
  },
  watch: {
    'form.name': function () {
      const debouncedGetSuggestions = debounce(this.getSuggestions, 500);
      debouncedGetSuggestions();
    },
    'typeahead.selected': function () {
      if (this.typeahead.include_id === true) {
        this.form[this.typeahead.id_field] = this.typeahead.selected.id;
      }
    },
  },
};

export default TypeaheadMixin;
