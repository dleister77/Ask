const typeahead2 = ('typeahead2', {
    props: {
        name: {
            type: String,
            required: true,
        },
        placeholder: {
            type: String,
            required: false,
        },
        readonly: {
            type: Boolean,
            required: false,
            default: false,
        },
        value: {
            type: String,
            required: false,
            default: "",
        },
        type: {
            type: String,
            required: false,
            default: "text"
        },
        url: "",
        filter: {},
    },
    computed:{
        query_string: function(){
            let qs = Object.entries(this.filter).map(function([key,value]){
                        return `${key}=${encodeURIComponent(value)}`});
            qs.push(`name=${encodeURIComponent(this.q)}`)
            return `?${qs.join('&')}`;
        },
        query_url: function(){
            return this.url + this.query_string
        },
    },
    data: function(){
        return {
            id:"",
            q: "",
            style: {},
            suggestions: [],
        }
    },
    inheritAttrs: false,
    methods:{
        getSuggestions: function(){
            let results;
            axios.get(this.query_url)
                .then(function(response){
                        results = response.data;
                })
                .catch(function(error){
                    console.log(error);
                    results = [];
                });
            this.suggestions = results;
        },
        updateValue: function(value){
            this.$emit('input', value);
        },
    },
    mounted: function(){
        let inputEl = $('.globalSearchInput input');
        inputEl.typeahead(
            {
                minLength: 1,
                highlight: true,
                classNames: {
                    menu: 'tt-menu form-control'
                }
            },
            {
                name: 'suggestions',
                source: [],
                limit: 5,
                display: function(item) {
                    return item.name;
                },
                templates: {
                    suggestion: (data) => {
                        return `<div>${data.name}</div>`;
                    },
                },
            }
        );
        inputEl.on('typeahead:select', (e, item) => {
            this.q = item.name;
            this.id = item.id;
        })
    },
    template: `
    <div class="globalSearchInput">
            <input
                type="text"
                class="form-control"
                placeholder="Search for a name..."
                v-bind:id="name"
                v-bind="$props"
                v-model.trim="q"
                v-on:input="getSuggestions"
                v-on:change="updateValue($event.target.value)"
                />
    </div>
    `,
    watch: {
        id: function(newVal, oldVal){
            this.$emit('id-change', {name: 'id-change', value: newVal});
        }
    }
})

export default typeahead2;