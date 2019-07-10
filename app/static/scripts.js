

function is_equal(x, y){
    if (x == y){
        return true;
    }
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

function ajaxModalPost(urltarget, success_message, failure_message){
    addcsrf();
    data=$(".modalinput").serialize();
    console.log("logged data: ", data)
    var parameters = {
        url: urltarget,
        type: "POST",
        data: data,
        dataType: "json"
    };
    $.ajax(parameters)
    .done(function(data){
        if (data['message'] == "success"){
            $("#modal_id").modal("hide");
            alert(success_message)
        } else if (data['message'] == "failure"){
            errorList = []
            Object.keys(data['errors']).forEach(function(key) {
                errorList.push(data['errors'][key])
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
    s.addEventListener("click", function(event){
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
function provider_get(){
    var c = document.getElementById("provider_category");
    c.addEventListener("click", function(event){
        var url = '/providerlist'
        var category = {"category": c.value}
        if (c.required == true){
            Object.assign(category, {"optional": true})
        }
        $.getJSON(url, category, function(data) {
            d = data;
            var provider_list = document.getElementById("provider_name");
            //remove existing options
            while (provider_list.hasChildNodes()){
                provider_list.removeChild(provider_list.firstChild);
            }
            for (var i = 0; i < data.length; i++){
                //append child option element to it with above as content
                var option = document.createElement('option');
                option.textContent = d[i].name;
                option.value = d[i].id;
                provider_list.appendChild(option);

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
            for (i=0; i < filter_ids.length; i++){
                key_name = filter_ids[i];
                value = document.getElementById(key_name).value;
                search_criteria[key_name] = value;
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
function autocomplete_by_id(selector_id, url, label_fields, value_field, filter_ids, submit_id, validation_message){
    var array = [];
    var array_full = [];
    var array_values = [];
    var array_detailed = [];
    $(selector_id).autocomplete({
        autoFocus: true,
        minLength: 1,
        delay: 200,
        source: function(request, response){
            search_criteria = {name: request.term};
            for (i=0; i < filter_ids.length; i++){
                key_name = filter_ids[i];
                value = document.getElementById(key_name).value;
                search_criteria[key_name] = value;
            }
            $.getJSON(url, search_criteria, function(data){
                    array = [];
                    var array_labels = [];
                    var array_values = [];
                    var array_detailed = [];
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
    var url = "/provider/list/autocomplete";
    var selector_id = "#review_name";
    var label_fields = ["name", "line1", "city", "state"];
    var value_field = "name";
    var filter_ids = ['category', 'state', 'city'];
    var submit_id = "review_submit";
    var validation_message = "Please choose a name from the list.";
    autocomplete_by_id(selector_id, url, label_fields, value_field, filter_ids,
                       submit_id, validation_message);

}

function initNetwork(jquery){
    //create function scope variables to be used for converting chosen name to user_id
    var friend_array = [];
    var friend_array_full = [];
    var friend_array_detailed =[];
    var friend_array_values =[];
    var group_array = [];
    var group_array_full = [];
    var group_array_values = [];
    var group_array_detailed = [];

    //autcomplete group name using jquery autocomplete ui: https://api.jqueryui.com/autocomplete/
    $("#group_name").autocomplete({
        autoFocus: true,
        minLength: 1,
        delay: 200,
        source: function(request, response){
            group_array = [];
            group_array_values = [];
            group_array_full = [];
            group_array_detailed = [];
            $.getJSON("/groupsearch", {"name":request.term}, function(data){
                    $.each(data, function(key, value){
                        group_array.push({"label":value.name, "value":value.name});
                        group_array_full.push(value.name);
                        group_array_values.push(value.name.toLowerCase());
                        group_array_detailed.push({key:value});
                    });
                    response(group_array);
            }); 
        },
        //enter group id into hidden input field
        select: function(event, ui){
            var i = group_array_full.indexOf(ui.item.label);
            $("#group_value").val(group_array_detailed[i].key.id);
        }       
    });


    //check submitted input vs autocomplete array
    function valcheck(array,input,msg){
        if (array.includes(input.value.toLowerCase()) == false){
            input.setCustomValidity(msg);
            check_validity(input);
        }else{
            input.setCustomValidity("");
            check_validity(input);
        }
    }

    //forces group search input to use value from autocomplete dropdown
    $("#submit-group-add").on("click", function(event){
        input = document.getElementById("group_name")
        valcheck(group_array_values, input, "Please choose group name from list or add group below.");
        $("#submit-group-add").unbind("click");
        $("#group_name").on("blur", function(event){
            valcheck(group_array_values, input,"Please choose group name from list or add group below.");
        });
    });

    //autocomplete friend name using jquery autocomplete ui: https://api.jqueryui.com/autocomplete/
    $("#friend_name").autocomplete({
        autoFocus: true,
        minLength: 1,
        delay: 200,
        source: function(request, response){
            friend_array=[];
            friend_array_full = [];
            friend_array_values = [];
            friend_array_detailed = [];
            $.getJSON("/friendsearch", {"name":request.term}, function(data){
                    $.each(data, function(key, value){
                        var full_description = [];
                        description = (value.first_name + " " + value.last_name + ", "+value.city +", "+ value.state);
                        name = (value.first_name + " " + value.last_name);
                        //label is what is shown in selector menu, value goes into input box
                        friend_array.push({"label":description, "value":name});
                        //used to check that values from list are selected in val check
                        friend_array_values.push(name.toLowerCase());
                        //used to find index of choice selected
                        friend_array_full.push(description);
                        //sets hidden input field to id
                        friend_array_detailed.push({key:value});
                    });
                    response(friend_array);
            });
        },
        //enter user_id into hidden input field
        select: function(event, ui){
            var i = friend_array_full.indexOf(ui.item.label);
            $("#friend_value").val(friend_array_detailed[i].key.id);
        }
    });

    //forces friend search input to use value from autocomplete dropdown
    $("#submit-friend-add").on("click", function(event){
        input = document.getElementById("friend_name")
        valcheck(friend_array_values, input, "Please choose friend name from list");
        $("#submit-friend-add").unbind("click");
        $("#friend_name").on("blur", function(event){
            valcheck(friend_array_values, input,"Please choose friend name from list");
        });
    });
}
function initSearch(jquery){
    var name, groups, friends;
    $(".bizlink").on("click", function(event){
        var name = this.text;
        var category =$("#category_name").val();
        var friends = $("#friends").prop("checked")
        var groups =  $("#groups").prop("checked")
        var zip = this.closest(".biz_rating").querySelector(".zip_code").innerText;
        var info = {"name":name, "category_name":category, "friends":friends, "groups":groups,"zip_code":zip}
        var query = "?"+$.param(info);
        this.search = query;

    });
    category_id = "category"
    sector_id = "sector"
    category_get(category_id=category_id, sector_id=sector_id);
    url = '/provider/list/autocomplete'
    id = "#provider_name"
    filter_ids = ['category', 'city', 'state']
    auto_complete(id, url, 'name', filter_ids);

}


function toggle_fields(unknown, target_ids){
    msg = document.getElementById("toggle_message")
    if(unknown.checked == true){
        msg.hidden = false;
        for(var i = 0; i < target_ids.length; i++){
            field = document.getElementById(target_ids[i]);
            field.hidden = true;
            field.parentNode.parentNode.hidden = true;
        }
    }else if (unknown.checked == false){
        msg.hidden = true;
        for(var i = 0; i < target_ids.length; i++){
            field = document.getElementById(target_ids[i]);
            field.hidden = false;
            field.parentNode.parentNode.hidden = true;
        }          
    }
}

//JS for provider add form
function initProviderAdd(jquery){
    category_get(category_id="category", sector_id="sector")
    //select unknown, line1, line2, zip
    unknown = document.getElementById("addressUnknown");
    target_ids = ["address-line1", "address-line2", "address-zip"]
    unknown.addEventListener("input", function(){
        toggle_fields(unknown, target_ids);
    });

}


//execute when DOM loaded
$(document).ready(function(){
    if( $("#submit-register").length){
        $(document).ready(initRegister);

    } else if ( $("#review_form").length){
        $(document).ready(initReview);

    } else if ($("#network").length){
        $(document).ready(initNetwork);
    } else if ($("#providersearch").length){
        $(document).ready(initSearch);
    } else if ($("#provideraddform").length){
        $(document).ready(initProviderAdd);
    } 
});