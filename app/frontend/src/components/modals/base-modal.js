const BaseModal = {
  delimiters: ['[[', ']]'],
  props: {
    title: {
      type: String,
      required: false,
    },
    modal_id: {
      type: String,
      required: true,
    },
    show_modal: {
      type: Boolean,
      required: true,
    },
    hide_modal: {
      type: Boolean,
      required: true,
    },
  },
  methods: {
    emit_hide() {
      this.$emit('modal_hide');
    },
    emit_hidden() {
      this.$emit('modal_is_hidden');
    },
    emit_show() {
      this.$emit('modal_show');
    },
    emit_shown() {
      this.$emit('modal_is_shown');
    },
    async hide() {
      await $(this.$refs.vuemodal).modal('hide');
      $('.modal-backdrop').remove();
    },
    async show() {
      await $(this.$refs.vuemodal).modal('show');
    }
  },
  mounted() {
    $(this.$refs.vuemodal).on('hide.bs.modal', this.emit_hide);
    $(this.$refs.vuemodal).on('hidden.bs.modal', this.emit_hidden);
    $(this.$refs.vuemodal).on('show.bs.modal', this.emit_show);
    $(this.$refs.vuemodal).on('shown.bs.modal', this.emit_shown);
  },
  watch: {
    show_modal(newVal) {
      if (newVal === true) {
        this.show();
      }
    },
    hide_modal(newVal) {
      if (newVal === true) {
        this.hide();
      }
    },
  },
  template: `
  <div>
      <div class="modal fade"
          :id="modal_id"
          ref="vuemodal"
          tabindex="-1"
          role="dialog">
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
  `,
};

export default BaseModal;
