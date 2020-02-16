import Vue from 'vue';
import typeahead_mixin from '../../components/typeahead_mixin';


const friendAdd = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    mixins: [typeahead_mixin],
    data: {
        urls: links,
        typeahead: {
            include_id: false,
        }
    },
    methods: {
        suggestionSerializer: function(person){
            return `${person.first_name} ${person.last_name}, ${person.city} ${person.state}`
        }
    },
});

export default friendAdd;