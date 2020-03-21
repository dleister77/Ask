import Vue from 'vue';
import typeahead_mixin from '../../components/forms/typeahead_mixin';



const groupAdd = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    mixins: [typeahead_mixin],
    data: {
        typeahead: {
            include_id: false,
        },
        urls: links,
    },
});

export default groupAdd;