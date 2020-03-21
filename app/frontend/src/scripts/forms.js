import axios from 'axios';
import { len } from 'vuelidate/lib/validators/common';

let category_get_url = '/categorylist';
let sector_get_url = '/sectorlist';


function categoryGet(url, sector, category_id){
    axios.get(url, {
        params: {
            sector: sector,
        },
    })
    .then(function(response) {
        updateSelectFieldOptions(response, category_id);
    })
    .catch(function(error){
        console.log(error);
    });
}

async function getCategoryList(sector=null){
    try {
        let response = await axios.get(category_get_url, {
                        params: {
                            sector: sector,
                        },
        });
        return response.data;
    } catch (error){
        console.log(`error: ${error}`);
    }
}

async function getSectorList(){

    try {
        let response = await axios.get(sector_get_url)
        return response.data;
    } catch (error) {
        console.log(error);
    }
}

function updateSelectFieldOptions(response, id){
    let selectField = document.getElementById(id);
    //remove existing options
    while (selectField.hasChildNodes()){
        selectField.removeChild(selectField.firstChild);
    }
    for (let item of response.data){
        //append child option element to it with above as content
        var option = document.createElement('option');
        option.textContent = item.name;
        option.value = item.id;
        selectField.appendChild(option);
    }    
}

function makeForm(object){
    let form = new FormData();
    Object.entries(object).forEach(([k,v]) => form.set(k,v));
    return form;
}

function postForm(path, params, method='post'){
    const form = document.createElement('form');
    form.method = method;
    form.action = path;
    
    for (const key in params){
        if (params.hasOwnProperty(key)){
            const hidden_field = document.createElement('input');
            hidden_field.type = "hidden";
            hidden_field.name = key;
            hidden_field.value = params[key];

            form.append(hidden_field);
        }
    }

    document.body.appendChild(form);
    form.submit();
}

function reset_form(form_old) {
    let form_new = {};
    Object.entries(form_old).forEach(function([key, value]) {
        switch (typeof value) {
            case 'string':
                form_new[key] = "";
                break;
            case 'boolean':
                form_new[key] = false;
                break;
            case 'number':
                form_new[key] = 0;
                break;
            case 'undefined':
                form_new[key] = null;
            case 'object':
                if (value instanceof Array) {
                    form_new[key] = Array(0);
                } else if (value == null) {
                    form_new[key] = null;
                } else if (len(Object.keys(value)) > 0) {
                    form_new[key] = reset_form(value);
                } else {
                    form_new[key] = null;
                }
                break;
        }
    });
    return form_new;
}

function is_object_literal(value) {
    if (typeof value != 'object' || value instanceof Array || value == null ){
        return false;
    }
    else if ( len(Object.keys(value)) > 0 ) {
        return true;
    } else {
        return false;
    }
}

function set_form(form_presets, form) {
    Object.entries(form_presets).forEach(function([key, value]) {
        if(is_object_literal(value)){
                form[key] = set_form(value, form[key]);
        } else {
            form[key] = value;
        }
    });
    return form;
}

export {categoryGet, getCategoryList, getSectorList, makeForm, postForm, reset_form, set_form};