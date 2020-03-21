import _ from 'lodash';

import form_mixin from './forms/form_mixin'
import ErrorMessage from './forms/error-message';
import form_input_select from './forms/form-input-select';
import FormTextbox from './forms/form-textbox';
import FormInput from './forms/form-input';
import FormInputCheckbox from './forms/form-input-checkbox';
import FormInputSelectMultiple from './forms/form-input-select-multiple';
import {states} from '../../supporting/states';

import {getCategoryList, getSectorList} from '../scripts/forms';
import {isEmpty, telephone} from '../scripts/validators';

import required from 'vuelidate/lib/validators/required';
import requiredIf from 'vuelidate/lib/validators/requiredIf';
import email from 'vuelidate/lib/validators/email';
import or from 'vuelidate/lib/validators/or';

let form_suggestion = {
    components: {
        'error-message': ErrorMessage,
        'form-input': FormInput,
        'form-textbox': FormTextbox,
        'form-input-checkbox': FormInputCheckbox,
        'form-input-select': form_input_select,
        'form-input-select-multiple': FormInputSelectMultiple,

    },
    mixins: [form_mixin],
    computed: {},
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
                    line1: "",
                    line2: "",
                    city: "",
                    state: "",
                    zip: "",
                    coordinate_error: false,
                },
                contact_info_updated: false,
                email: "",
                website: "",
                telephone:"",
                other: "",
            },
            options: {
                states: states,
                sectors: [],
                categories: [],
            }
        }
    },
    delimiters: ["[[", "]]"],
    props: {}, //set by mixin
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
                coordinate_error: {
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
        get_sector_list: async function() {
            let s = await getSectorList();
            return s;
        },
        get_category_list: async function(sector=null) {
            let c = await getCategoryList(sector);
            return c
        },
    },
    created: async function() {
        this.options.sectors = await this.get_sector_list();
        this.options.categories = await this.get_category_list();
    },
    watch: {
        'form.sector': {
            handler: async function(new_val){
                if (new_val != 0) {
                    this.options.categories = await this.get_category_list(new_val);
                }
            },

        },
    },
    template: `
    <div>
        <form :id="form_id" :action="url" method="POST">
            <input name="csrf_token" type="hidden" :value="form_presets.csrf_token">
            <input name='id' type="hidden" :value="form_presets.id">
            
            <form-input
                name="name"
                :readonly="true"
                :required="true"
                :validator="$v.form.name"
                v-model="$v.form.name.$model"
                :server_side_errors="server_side_errors.name">
                Business Name
            </form-input>
            
            <form-input-checkbox
                name="is_not_active"
                :required="true"
                :validator="$v.form.is_not_active"
                v-model="$v.form.is_not_active.$model"
                :server_side_errors="server_side_errors.is_not_active">
                Check if business is permanently closed.
            </form-input-checkbox>
            
            <form-input-checkbox
                name="category_updated"
                :required="true"
                :validator="$v.form.category_updated"
                v-model="$v.form.category_updated.$model"
                :server_side_errors="server_side_errors.category_updated">
                Check if business sector/categories need to be updated.
            </form-input-checkbox>
            <form-input-select
                v-if="form.category_updated"
                name="sector"
                :options="options.sectors"
                :validator="$v.form.sector"
                v-model="$v.form.sector.$model"
                :server_side_errors="server_side_errors.sector">
            Sector
          </form-input-select>            
            <form-input-select-multiple
                v-if="form.category_updated"
                name="category"
                :options="options.categories"
                :validator="$v.form.category"
                v-model="$v.form.category.$model"
                :server_side_errors="server_side_errors.category">
            Category
          </form-input-select-multiple>


            <form-input-checkbox
                name="address_updated"
                :required="true"
                v-model="$v.form.address_updated.$model"
                :validator="$v.form.address_updated"
                :server_side_errors="server_side_errors.address_updated">
                Check if address/location is incorrect.
            </form-input-checkbox>
            <form-input-checkbox
                v-if="form.address_updated"
                name="coordinate_error"
                :required="true"
                :validator="$v.form.address.coordinate_error"
                v-model="$v.form.address.coordinate_error.$model"
                :server_side_errors="server_side_errors.address.coordinate_error">
                Check if map coordinates are incorrect.
            </form-input-checkbox>
            <form-input
                v-if="form.address_updated"
                name="line1"
                :required="true"
                :validator="$v.form.address.line1"
                v-model="$v.form.address.line1.$model"
                :server_side_errors="server_side_errors.address.line1">
                Street Address
            </form-input>
            <form-input
                v-if="form.address_updated"
                name="line2"
                :required="false"
                v-model="form.address.line2"
                :server_side_errors="server_side_errors.address.line2">
                Address Line 2
            </form-input>
            <form-input
                v-if="form.address_updated"
                name="city"
                :required="true"
                :validator="$v.form.address.city"
                v-model="$v.form.address.city.$model"
                :server_side_errors="server_side_errors.address.city">
                City
            </form-input>
            <form-input-select
                v-if="form.address_updated"
                name="state"
                :options="options.states"
                :validator="$v.form.address.state"
                :value="form.address.state"
                v-model.trim="$v.form.address.state.$model"
                :server_side_errors="server_side_errors.address.state">
            State
          </form-input-select>
            <form-input
                v-if="form.address_updated"
                name="zip"
                :required="true"
                :validator="$v.form.address.zip"
                v-model="$v.form.address.zip.$model"
                :server_side_errors="server_side_errors.address.zip">
                Zip Code
            </form-input>                                            

            <form-input-checkbox
                name="contact_info_updated"
                :required="true"
                v-model="$v.form.contact_info_updated.$model"
                :validator="$v.form.contact_info_updated"
                :server_side_errors="server_side_errors.contact_info_updated">
                Check if email, website or telephone are incorrect.
            </form-input-checkbox>
            <form-input
                v-if="form.contact_info_updated"
                name="email"
                :required="false"
                :validator="$v.form.email"
                v-model="$v.form.email.$model"
                :server_side_errors="server_side_errors.email">
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
                v-model="$v.form.website.$model"
                :server_side_errors="server_side_errors.website">
                Website
            </form-input>  
            <form-input
                v-if="form.contact_info_updated"
                name="telephone"
                :required="false"
                :validator="$v.form.telephone"
                v-model="$v.form.telephone.$model"
                :server_side_errors="server_side_errors.telephone">
                Telephone
                <template v-slot:errors>
                    <error-message
                    :field="$v.form.telephone"
                    validator="or">
                    Telephone number must be 10 digits long.
                    </error-message>
                </template>
            </form-input>                                      

            <form-textbox
                name='other'
                v-model.trim="form.other"
                :required="false"
                :server_side_errors="server_side_errors.other">
                Other
            </form-textbox>

            <button
                :id="form_id + '_submit'"
                class="btn btn-primary btn-block submit"
                type="submit"
                v-on:click.prevent="submit">
                Submit
            </button>
        </form>
    </div>
    
    `
}
export default form_suggestion;