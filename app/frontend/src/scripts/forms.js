import axios from 'axios'

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
export {categoryGet};