import Vue from 'vue';
import Vuelidate from 'vuelidate';

import ErrorMessage from './error-message';
import form_input_group from './form-input-group';
import form_input_select from './form-input-select';
import form_textbox from './form-textbox';
import FormInput from './form-input';
import FormInputCheckbox from './form-input-checkbox';
import FormInputSelectMultiple from './form-input-select-multiple';
import {states} from '../../supporting/states';

import {categoryGetList, getSectorList} from './../scripts/forms';
import {isEmpty, telephone} from './../scripts/validators';



import required from 'vuelidate/lib/validators/required';
import requiredIf from 'vuelidate/lib/validators/requiredIf';
import email from 'vuelidate/lib/validators/email';
import or from 'vuelidate/lib/validators/or';


Vue.use(Vuelidate);

let form_message_correction = {
    components: {
        'error-message': ErrorMessage,
        'form-input': FormInput,
        'form-input-group': form_input_group,
        'form-textbox': form_textbox,
        'form-input-checkbox': FormInputCheckbox,
        'form-input-select': form_input_select,
        'form-input-select-multiple': FormInputSelectMultiple,

    },
    computed: {

    },
    data: function(){
        return {
            form: {
                csrf_token: "",
                id: "",
                name: "",
                is_not_active: false,
                category_updated: false,
                sector: "",
                category: "",
                address_updated: false,
                address: {
                    is_coordinate_error: false,
                    line1: "",
                    line2: "",
                    city: "",
                    state: "",
                    zip: ""
                },
                contact_info_updated: false,
                email: "",
                website: "",
                telephone:"",
                other: "",
            },
            states: states,
            sectors: [],
            categories: [],
        }
    },
    delimiters: ["[[", "]]"],
    props: {
        form_presets: {
            type: Object,
            required: false,
        },
        url: {
            type: String,
            required: true,
        },
        reset_form: {
            type: Boolean,
            required: false,
        }
    },
    validations: {
        form: {
            id: {
                required,
            },
            name: {
                required,
            },
            is_not_active: {
                required,
            },
            category_updated: {
                required,
            },
            sector: {
                required: requiredIf(function(){
                    return this.form.category_updated;
                }),
            },
            category: {
                required: requiredIf(function(){
                    return this.form.category_updated;
                }),
            },
            address_updated: {
                required,
            },
            address: {
                is_coordinate_error: {
                    required: requiredIf(function(){
                        return this.form.address_updated;
                    }),
                },                
                line1: {
                    required: requiredIf(function(){
                        return this.form.address_updated;
                    })
                },
                city: {
                    required: requiredIf(function(){
                        return this.form.address_updated;
                    }),
                },
                state: {
                    required: requiredIf(function(){
                        return this.form.address_updated;
                    }),
                },
                zip: {
                    required: requiredIf(function(){
                        return this.form.address_updated;
                    }),
                },
            },
            contact_info_updated: {
                required,
            },
            email: {
                or: or(isEmpty, email),
            },
            website: {
            },
            telephone: {
                or: or(isEmpty, telephone),                
            },
        },
    },
    methods: {
        resetForm: function() {
            this.$v.$reset();
            Object.keys(this.form).forEach((key)=> this.form[key] = (typeof this.form[key] == 'boolean') ? false : "");
        },
        get_address_updated: function() {
            return this.form.address_updated;
        }
        
    },
    created: async function() {
        let s = await getSectorList();
        this.sectors = s;
    },
    watch: {
        'form_presets': {
            handler: function(new_val) {
            Object.entries(this.form_presets).forEach(([key,value])=>this.form[key]=value);
            },
            deep: true,
        },
        'reset_form': function(new_val) {
            if (new_val==true) {
                this.resetForm();
                this.$emit('form_is_reset')
            }
        },
        'form.sector': {
            handler: async function(new_val){
                let c = await categoryGetList(new_val);
                this.categories = c;
            },
        },
        '$v.$invalid': function(new_val) {
            let is_valid = !new_val;
            this.$emit('form_is_valid', is_valid);
        }
    },
    template: `
    <div>
        <form id = "message-form" v-bind:action="url" method="POST">
            <input name="csrf_token" type="hidden" :value="form_presets.csrf_token">
            <input name='id' type="hidden" :value="form_presets.id">
            
            <form-input
                name="name"
                :readonly="true"
                :required="true"
                :validator="$v.form.name"
                v-model="$v.form.name.$model">
                Business Name
            </form-input>
            
            <form-input-checkbox
                name="is_not_active"
                :required="true"
                :validator="$v.form.is_not_active"
                v-model="$v.form.is_not_active.$model">
                Check if business is permanently closed.
            </form-input-checkbox>
            
            <form-input-checkbox
                name="category_updated"
                :required="true"
                :validator="$v.form.category_updated"
                v-model="$v.form.category_updated.$model">
                Check if business sector/categories need to be updated.
            </form-input-checkbox>
            <form-input-select
                v-if="form.category_updated"
                name="sector"
                :options="sectors"
                :validator="$v.form.sector"
                v-model="$v.form.sector.$model"
                :value="form.sector">
            Sector
          </form-input-select>            
            <form-input-select-multiple
                v-if="form.category_updated"
                name="category"
                :options="categories"
                :validator="$v.form.category"
                v-model="$v.form.category.$model"
                :value="form.category">
            Category
          </form-input-select-multiple>


            <form-input-checkbox
                name="form.address_updated"
                :required="true"
                v-model="$v.form.address_updated.$model"
                :validator="$v.form.address_updated">
                Check if address/location is incorrect.
            </form-input-checkbox>
            <form-input-checkbox
                v-if="form.address_updated"
                name="is_coordinate_error"
                :required="true"
                :validator="$v.form.address.is_coordinate_error"
                v-model="$v.form.address.is_coordinate_error.$model">
                Check if map coordinates are incorrect.
            </form-input-checkbox>
            <form-input
                v-if="form.address_updated"
                name="line1"
                :required="true"
                :validator="$v.form.address.line1"
                v-model="$v.form.address.line1.$model">
                Street Address
            </form-input>
            <form-input
                v-if="form.address_updated"
                name="line2"
                :required="false"
                v-model="form.address.line2">
                Address Line 2
            </form-input>
            <form-input
                v-if="form.address_updated"
                name="city"
                :required="true"
                :validator="$v.form.address.city"
                v-model="$v.form.address.city.$model">
                City
            </form-input>
            <form-input-select
                v-if="form.address_updated"
                name="address-state"
                :options="states"
                :validator="$v.form.address.state"
                :value="form.address.state"
                v-model.trim="$v.form.address.state.$model">
            State
          </form-input-select>
            <form-input
                v-if="form.address_updated"
                name="zip"
                :required="true"
                :validator="$v.form.address.zip"
                v-model="$v.form.address.zip.$model">
                Zip Code
            </form-input>                                            

            <form-input-checkbox
                name="form.contact_info_updated"
                :required="true"
                v-model="$v.form.contact_info_updated.$model"
                :validator="$v.form.contact_info_updated">
                Check if email, website or telephone are incorrect.
            </form-input-checkbox>
            <form-input
                v-if="form.contact_info_updated"
                name="email"
                :required="false"
                :validator="$v.form.email"
                v-model="$v.form.email.$model">
                Email Address
                <template v-slot:errors>
                    <error-message
                    :field="$v.form.email"
                    validator="or">
                    Invalid email address
                    </error-message>
                </template>

            </form-input>  
            <form-input
                v-if="form.contact_info_updated"
                name="website"
                :required="false"
                :validator="$v.form.website"
                v-model="$v.form.website.$model">
                Website
            </form-input>  
            <form-input
                v-if="form.contact_info_updated"
                name="telephone"
                :required="false"
                :validator="$v.form.telephone"
                v-model="$v.form.telephone.$model">
                Telephone
                <template v-slot:errors>
                <error-message
                :field="$v.form.telephone"
                validator="or">
                Telephone number must be 10 digits long.
                </error-message>
            </template>
            </form-input>                                      

            <div class="form-group">
            <form-textbox
                name='other'
                v-model.trim="form.other"
                :required="false">
                Other
            </form-textbox>
        </div>
        </form>
    </div>
    
    `
}
export default form_message_correction;