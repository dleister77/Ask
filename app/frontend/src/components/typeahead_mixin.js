import VueBootstrapTypeahead from 'VueBootstrapTypeahead';
import _ from 'lodash';



const typeahead_mixin = {
    components: {
        'vue-bootstrap-typeahead': VueBootstrapTypeahead,
    },
    data: function() {
        return {
            form: {
                id: "",
                name: "", 
            },
            typeahead: {
                suggestions: [],
                selected: null,
                include_id: true,
                name_field: 'name',
                id_field: 'id',
            },
            urls: links,
        }
    },
    methods:{
        makeQueryUrl: function(){
            let input = this.form[this.typeahead.name_field];
            return `${this.urls.autocomplete}?name=${encodeURIComponent(input)}`
        },
        getSuggestions: async function(){
            const res = await fetch(this.makeQueryUrl());
            const suggestions = await res.json();
            this.typeahead.suggestions = suggestions;
        },
        suggestionSerializer: function(item){
            return `${item.name}`
        }
    },        
    watch: {
        'form.name': function(val){
            const debouncedGetSuggestions = _.debounce(this.getSuggestions, 500);
            debouncedGetSuggestions();
        },
        'typeahead.selected': function(){
            if (this.typeahead.include_id == true){
                this.form[this.typeahead.id_field] = this.typeahead.selected.id
            }
        }
    }
}

export default typeahead_mixin;