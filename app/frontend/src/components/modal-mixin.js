
import modal from './modal';

let modal_mixin = {
    components: {
        'modal': modal,
    },
    delimiters: ["[[", "]]"],
    props: {
        title: {
            type: String,
            required: false,
        },
        modal_id: {
            type: String,
            required: false,
            default: 'vue_modal'
        }
    },
    methods: {
        toggleModal: function(){
            this.show = !this.show;
            let id = `#${this.modal_id}`;
            jQuery(id).modal('toggle');
        },
    },
}

export default modal_mixin;