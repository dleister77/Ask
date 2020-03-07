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

export {categoryGet, makeForm, postForm};