

function is_equal(x, y){
    if (x == y){
        return true;
    }
}

function formDataFromObject(object){
    let form = new FormData()
    for (let [key, value] of Object.entries(object)){
        form.append(key, value);
    }
    return form;
}

function Page(startingPage) {
    this.active = startingPage,
    this.previous_pages = [],
    this.navigate_next = navigate_next,
    this.navigate_back = navigate_back
}

function navigate_next(next_page_id){
    toggle_visibility(next_page_id, this.active);
    this.previous_pages.push(this.active);
    this.active = next_page_id;
    toggle_move_visibility();
    toggle_new_message_visibility();
}

function navigate_back(previous_page_id){
    toggle_visibility(previous_page_id, this.active);
    this.active = previous_page_id;
    if (page.active == 'inbox' && document.querySelectorAll('input.select:checked').length == 0){
        messages.selected_ids = [];
    }
    toggle_move_visibility();
    toggle_new_message_visibility();
}

function select_all_rows(select_all){
    for (let row of messages.folder_rows){
        row.querySelector(".select").checked = select_all.checked;
    }
}

function toggle_move_visibility(){
    let display_status = (messages.selected_ids.length > 0 && page.active != 'message_send') ? "block" : "none";
    let links_to_hide = document.getElementsByClassName("action_move");
    for (let link of links_to_hide){
        link.style.display = display_status;
    }
}

function toggle_new_message_visibility(){
    let display_status = (page.active == 'inbox') ? "block" : "none"
    let links_to_hide = document.getElementsByClassName("action_inbox");
    for (let link of links_to_hide){
        link.style.display = display_status;
    }
}

function toggle_visibility(id_to_show, id_to_hide){
    document.getElementById(id_to_hide).hidden = true;
    document.getElementById(id_to_show).hidden = false;   
}

function addcsrf(){
    var csrf_token = document.getElementById("csrf_token").value;
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });
}

function post(path, params, method='post'){
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

function ajaxSend(urltarget, formID){
    addcsrf();
    data=$(`#${formID}`).serialize();
    var parameters = {
        url: urltarget,
        type: "POST",
        data: data,
        dataType: "json"
    };
    $.ajax(parameters)
    .done(function(data){
        if (data['status'] == "success"){
            alert("Message sent.");
        } else if (data['status'] == "failure"){
            errorList = []
            Object.keys(data['errorMsg']).forEach(function(key) {
                errorList.push(data['errorMsg'][key])
            });
            errors = errorList.join('\n')
            alert("Message failed to send.  Please correct errors:" + "\n" + errors)
        }

    })
    .fail(function(data){
        console.log("failed")
        alert("Message failed to send.");
    });
}

function ajaxModalPost(urltarget, modalID, success_message, failure_message){
    addcsrf();
    data=$(".modalinput").serialize();
    var parameters = {
        url: urltarget,
        type: "POST",
        data: data,
        dataType: "json"
    };
    $.ajax(parameters)
    .done(function(data){
        if (data['status'] == "success"){
            $("#" + modalID).modal("hide");
            alert(success_message);
        } else if (data['status'] == "failure"){
            errorList = []
            Object.keys(data['errorMsg']).forEach(function(key) {
                errorList.push(data['errorMsg'][key])
            });
            errors = errorList.join('\n')
            alert(failure_message + "\n" + errors)
        }

    })
    .fail(function(data){
        console.log("failed")
        alert(failure_message);
    });
}

function valcheckListener(formID){
    errors = []
    var form = document.getElementById(formID);
    var inputs = form.querySelectorAll("input, select, textarea");
    var submit = form.querySelector(".submit");
    inputs.forEach(function(input){
        check_validity(input);
        if (input.classList.contains("error") == true){
            errors.push("error")
        }
        input.addEventListener("blur", function(event){
            check_validity(input);
            if (input.classList.contains("error") == false){
                errors.pop()
            }
        });
    });
    console.log("Errors: " + errors)
    return errors;
}

function check_validity(input){
    if (input.checkValidity() == false){
    input.classList.add("error");
    console.log("classList: " + input.classList)
    } else if (input.checkValidity() == true){
    input.classList.remove("error");
    console.log("removed classList: " + input.classList)
    }
}


function category_get(category_id="provider_category", sector_id="provider_sector"){
    var s = document.getElementById(sector_id);
    s.addEventListener("input", function(event){
        var url =  "/categorylist";
        var sector = {"sector": s.value};
        $.getJSON(url, sector, function(data) {
            d = data;
            var category_list = document.getElementById(category_id);
            //remove existing options
            while (category_list.hasChildNodes()){
                category_list.removeChild(category_list.firstChild);
            }
            for (var i = 0; i < data.length; i++){
                //append child option element to it with above as content
                var option = document.createElement('option');
                option.textContent = d[i].name;
                option.value = d[i].id;
                category_list.appendChild(option);

            }
        });
    });
}

function auto_complete(selector_id, url,field_name, filter_ids){

    $(selector_id).autocomplete({
        autoFocus: true,
        minLength: 1,
        delay: 200,
        source: function(request, response){
            search_criteria = {name: request.term};
            if(filter_ids != null){
                for (i=0; i < filter_ids.length; i++){
                    key_name = filter_ids[i];
                    value = document.getElementById(key_name).value;
                    search_criteria[key_name] = value;
                }
            }
            $.getJSON(url, search_criteria, function(data){
                    array = [];
                    $.each(data, function(key, value){
                        array.push({"label": value[field_name], "value":value[field_name]});
                    });
                    response(array);
            }); 
        },     
    });    
}
//like above, but saves id associated with selected field as value
function autocomplete_by_id(selector_id, url, label_fields, value_field, value_field_id, filter_ids, submit_id, validation_message){
    let array = [];
    let array_full = [];
    let array_labels = [];
    let array_values = [];
    let array_detailed = [];
    $(selector_id).autocomplete({
        autoFocus: true,
        minLength: 1,
        delay: 200,
        source: function(request, response){
            search_criteria = {name: request.term};
            for (let id of filter_ids){
                key_name = id;
                value = document.getElementById(key_name).value;
                search_criteria[key_name] = value;
            }
            $.getJSON(url, search_criteria, function(data){
                    array = [];
                    array_labels = [];
                    array_values = [];
                    array_detailed = [];
                    $.each(data, function(key, value){
                        var label = []
                        for (i=0; i < label_fields.length; i++){
                            label.push(value[label_fields[i]] + " ")
                        }
                        label = label.join(", ")
                        var input_value = value[value_field];
                        array.push({"label": label, "value": input_value});
                        //used to check that values from list are selected in val check
                        array_values.push(input_value.toLowerCase());
                        //used to find index of choice selected
                        array_labels.push(label);
                        //sets hidden input field to id
                        array_detailed.push({key:value});
                    });
                    response(array);
            }); 
        },
        select: function(event, ui){
            var i = array_labels.indexOf(ui.item.label);
            let val2save = array_detailed[i].key.id;
            $(value_field_id).val(array_detailed[i].key.id);
        }     
    });
    require_autocomplete(selector_id, submit_id, validation_message);
}

function require_autocomplete(selector_id, submit_id, validation_message){
    //forces search input to use value from autocomplete dropdown
    $(submit_id).on("click", function(event){
        input = document.getElementById(selector_id)
        valcheck(array_values, input, validation_message);
        $(submit_id).unbind("click");
        $(selector_id).on("blur", function(event){
            valcheck(array_values, input, validation_message);
        });
    });
}

function show(element){
    element.hidden = false;
    for (let child of element.children){
        show(child);
    }
}
function hide(element){
    element.hidden = true;
    for (let child of element.children){
        hide(child);
    }
}

function toggle_fields(toCheck, checkValue, toBeHiddenIDs=null, toBeVisibleID=null){
    if (toBeVisibleID != null){
        toBeVisible = document.getElementById(toBeVisibleID)
    }
    let value;
    if (toCheck.type == "select-one"){
        value = toCheck.value
        console.log("value: " + value)
    } else if (toCheck.type == 'checkbox'){
        value = toCheck.checked
    }
    if(value == checkValue){
        show(toBeVisible)
        if (toBeHiddenIDs != null){
            for(var i = 0; i < toBeHiddenIDs.length; i++){
                field = document.getElementById(toBeHiddenIDs[i]);
                field.hidden = true;
                field.parentNode.parentNode.hidden = true;
            }
        }
    }else if (value != checkValue){
        hide(toBeVisible)
        if (toBeHiddenIDs != null){
            for(var i = 0; i < toBeHiddenIDs.length; i++){
                field = document.getElementById(toBeHiddenIDs[i]);
                field.hidden = false;
                field.parentNode.parentNode.hidden = false;
            }          
        }
    }
}

function toggle_fields_required(toCheck, checkValue, toBeHiddenIDs=null, toBeVisibleID=null){
    if (toBeVisibleID != null){
        toBeVisible = document.getElementById(toBeVisibleID)
    }
    let value;
    if (toCheck.type == "select-one"){
        value = toCheck.value
        console.log("value: " + value)
    } else if (toCheck.type == 'checkbox'){
        value = toCheck.checked
    }
    if(value == checkValue){
        if (toBeHiddenIDs != null){
            for(var i = 0; i < toBeHiddenIDs.length; i++){
                field = document.getElementById(toBeHiddenIDs[i]);
                field.required = false;
                field.parentNode.parentNode.hidden = true;
            }
        }
    }else if (value != checkValue){
        if (toBeHiddenIDs != null){
            for(var i = 0; i < toBeHiddenIDs.length; i++){
                field = document.getElementById(toBeHiddenIDs[i]);
                field.hidden = true;
                field.parentNode.parentNode.hidden = false;
            }          
        }
    }
}

function request_location(toCheck, checkValue){
    let geoSuccess = function(position) {
        newPos = position;
        document.getElementById('gpsLat').value = newPos.coords.latitude;
        document.getElementById('gpsLong').value = newPos.coords.longitude;
      };
    let geoError = function(error) {
    console.log('Error occurred. Error code: ' + error.code);
    }
    let geoOptions = {
        maximumAge : 5 * 60 * 1000,
        timeout : 10 * 1000
    }

    if (toCheck.value == checkValue){
        navigator.geolocation.getCurrentPosition(geoSuccess, geoError, geoOptions)
    }
}

function validity_test(input){

}
function initRegister(jquery) {
    var s = document.getElementById("submit-register");
    var p = document.getElementById("password");
    var c = document.getElementById("confirmation");
    s.addEventListener("click", function(event) {
        if (p.value != c.value){
            c.setCustomValidity("passwords do not match");
        } else {
            c.setCustomValidity("");
        }
    });
    var forms = document.querySelectorAll("form");
    forms.forEach(function(form){
        var inputs = form.querySelectorAll("input, select, textarea");
        var submit = form.querySelector(".submit");
        submit.addEventListener("click", function(event){
            inputs.forEach(function(input){
                check_validity(input);
                input.addEventListener("blur", function(event){
                    check_validity(input);
                });
            });
        });
    });
}


function initReview (jquery) {
    var sector_id = "sector";
    var category_id = "category";
    category_get(category_id=category_id, sector_id=sector_id);
    var forms = document.querySelectorAll("form");
    forms.forEach(function(form){
        var inputs = form.querySelectorAll("input, select, textarea");
        var submit = form.querySelector(".submit");
        submit.addEventListener("click", function(event){
            inputs.forEach(function(input){
                check_validity(input);
                input.addEventListener("blur", function(event){
                    check_validity(input);
                });
            });
        });
    });
    //set up provider name autocomplete and validation
    // var url = "/provider/list/autocomplete";
    // var selector_id = "#review_name";
    // var label_fields = ["name", "line1", "city", "state"];
    // var value_field = "name";
    // var filter_ids = ['category', 'state', 'city'];
    // var submit_id = "review_submit";
    // var validation_message = "Please choose a name from the list.";
    // autocomplete_by_id(selector_id, url, label_fields, value_field, filter_ids,
    //                    submit_id, validation_message);

}


//execute when DOM loaded
$(document).ready(function(){
    if( $("#submit-register").length){
        $(document).ready(initRegister);

    } else if ( $("#review_form").length){
        $(document).ready(initReview);
});


const debounce = (callback, time = 250) => (...args) => {
    let interval;
    clearTimeout(
      interval,
      (interval = setTimeout(() => callback(...args), time))
    );
  };

function hello(){
    console.log("hello world");
}

const delayedHello = debounce(hello, 10000);
