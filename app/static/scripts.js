

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


function category_get(){
    var s = document.getElementById("provider_sector");
    s.addEventListener("click", function(event){
        var url =  "/categorylist";
        var sector = {"sector": s.value};
        $.getJSON(url, sector, function(data) {
            d = data;
            var category_list = document.getElementById("provider_category");
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
    category_get();
    var c = document.getElementById("provider_category");
    c.addEventListener("click", function(event){
        var csrf_token = document.getElementById("csrf_token").value;
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", csrf_token);
                }
            }
        });
        var parameters = {
            url: "/providerlist",
            data: {category: c.value},
            type: "POST",
            dataType: "json"
        };
        $.ajax(parameters).done(function(data) {
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
                        friend_array.push({"label":description, "value":name});
                        friend_array_values.push(name.toLowerCase());
                        friend_array_full.push(description);
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
    $("#submit_new_group").on("click", function(event){
        event.preventDefault();
        //first validate.  need to return errors
        errors = valcheckListener("modal_form_group")
        //if no errors do ajax modal post
        if (errors.length == 0){
            ajaxModalPost('/groupcreate', "Successfully added group", "Failed to add group.  Please correct the following errors: ");
        }
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
    category_get()
}
//JS for provider add form
function initProviderAdd(jquery){
    category_get()
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