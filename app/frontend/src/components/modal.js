
let modal = {
    delimiters: ["[[", "]]"],
    props: {
        title: {
            type: String,
            required: false,
        },
        modal_id: {
            type: String,
            required: true,
        }
    },
    methods: {
        emit_hide: function() {
            this.$emit('modal_hide');
        },
        emit_show: function() {
            this.$emit('modal_show');
        }
    },
    mounted: function(){
        $(this.$refs.vuemodal).on('hide.bs.modal', this.emit_hide);
        $(this.$refs.vuemodal).on('show.bs.modal', this.emit_show);
    },
    template: `
    <div>
        <div class="modal fade" ref="vuemodal" :id="modal_id" tabindex="-1" role="dialog">
            <div class="modal-dialog modal-md" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">[[ title ]]</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body px-5">
                        <slot name="body"></slot>
                    </div>
                    <div class="modal-footer">
                        <slot name="footer">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                        </slot>
                    </div>
                </div>
            </div>
        </div>
    </div>
    `
}

export default modal;