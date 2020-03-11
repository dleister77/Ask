import modal_message_correction from './modal-message-correction';


const modal_message_correction_mixin = {
    components: {
        "modal-message-correction": modal_message_correction,
    },
    delimiters: ['[[', ']]'],
    data: {
        activeBusiness: "",
        form_presets: {
            csrf_token: csrf,
            id: "",
            subject: "",
            address: "",
            address_status: "",
            sector: "",
            category: "",
            email: "",
            website: "",
            telephone: "",
        },
        urls: {
            send_message: "/provider/suggestion"
        },
    },
    methods: {
        setMessagePresets: function(event){
            let source = event.target;
            this.form_presets.id = source.dataset.id;
            this.form_presets.name = source.dataset.subject;
            this.setActiveBusiness(this.form_presets.id);
            this.form_presets.category = String(this.activeBusiness.category_ids).split(',').map(Number);
            this.form_presets.sector = Number(this.activeBusiness.sector_ids)
            this.form_presets.address = {
                line1: this.activeBusiness.line1,
                line2: this.activeBusiness.line2,
                city: this.activeBusiness.city,
                state: Number(this.activeBusiness.state_id),
                zip: this.activeBusiness.zip,
            };
            this.form_presets.email = this.activeBusiness.email;
            this.form_presets.website = this.activeBusiness.website;
            this.form_presets.telephone = this.activeBusiness.telephone;
        },
        resetFormPresets: function() {
            Object.keys(this.form_presets).forEach(function(key) {
                if (key != "csrf_token"){
                    this.form_presets[key] = "";
                }
            }, this);
        },
        setActiveBusiness: function(id) {
            //to be implemented by individual page
        }
    },
}
export default modal_message_correction_mixin;