const typeahead = ('typeahead', {
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
    },
    data: function(){
        return {
            id:"",
            q: "",
            suggestions: [],
            style: {},
        }
    },
    inheritAttrs: false,
    methods:{
        updateValue: function(value){
            this.$emit('input', value);
        },
    },
    mounted: function(){
        this.suggestions = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('full_name'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            identify: function(item){
                return item.id;
            },
            remote: {
                url: this.url + '?name=%QUERY',
                wildcard: '%QUERY'
            }

        });
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
                source: this.suggestions,
                limit: 5,
                display: function(item) {
                    return item.full_name;
                },
                templates: {
                    suggestion: (data) => {
                        return `<div>${data.full_name}</div>`;
                    },
                },
            }
        );
        inputEl.on('typeahead:select', (e, item) => {
            this.q = item.full_name;
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

export default typeahead;