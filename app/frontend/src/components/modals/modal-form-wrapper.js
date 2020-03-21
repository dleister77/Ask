import base_modal from './base-modal';
import form_wrapper_mixin from '../forms/form-wrapper-mixin';


let modal_form_wrapper = {
    components: {
        'base-modal': base_modal,
    },
    mixins: [form_wrapper_mixin],
    data: function(){
        return {
            show_modal: false,
            hide_modal: false,
        }
    },
    delimiters: ["[[", "]]"],
    props: {
        title: {
            type: String,
            required: true,
        },
        modal_id: {
            type: String,
            required: false,
            default: "ask-form-modal"
        },
    },
    methods: {
        prepare_modal_hide: function() {
            this.reset_form_values = true;
        },
        prepare_modal_show: function() {
            this.set_form_values = true;
        },
        do_show_modal: function() {
            this.show_modal = true;
        },
        do_hide_modal: function() {
            this.hide_modal = true;
        },
        mark_modal_shown: function() {
            this.show_modal = false;
        },
        mark_modal_hidden: function() {
            this.hide_modal = false;
        }
    },
    template: `
    <div>
        <base-modal
            :title="title"
            :modal_id="modal_id"
            :show_modal="show_modal"
            :hide_modal="hide_modal"
            @modal_hide="prepare_modal_hide"
            @modal_show="prepare_modal_show"
            @modal_is_hidden="mark_modal_hidden"
            @modal_is_shown="mark_modal_shown">

            <template v-slot:body>
                <slot name="default"
                    :reset_form_values="reset_form_values"
                    :set_form_values="set_form_values"
                    :form_presets="form_presets"
                    :url="url"
                    :mark_form_set="mark_form_set"
                    :mark_form_reset="mark_form_reset"
                    :do_hide_modal="do_hide_modal">
                </slot>
            </template>
        </base-modal>
    </div>
    
    `
}

export default modal_form_wrapper;