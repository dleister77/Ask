import axios from 'axios';

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

async function categoryGetList(sector=null){
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

    let response = await fetch(sector_get_url)
    let list = await response.json()
    return list;
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

export {categoryGet, categoryGetList, getSectorList, makeForm, postForm};