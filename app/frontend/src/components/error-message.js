let ErrorMessage = {
    props: {
        field: Object,
        validator: String,
    },
    computed: {
        isInvalid(){
            return !this.field[this.validator] && this.field["$dirty"];
        }
    },
    template: 
           `<div>
                <small v-if='isInvalid' class="form-error-message">
                <slot></slot>
                </small>
            </div>
            `
}

export default ErrorMessage;