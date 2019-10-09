

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

function initFriends(jquery){
    //create function scope variables to be used for converting chosen name to user_id
    var friend_array = [];
    var friend_array_full = [];
    var friend_array_values =[];
    var friend_array_detailed =[];
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
            $.getJSON(url, {"name":request.term}, function(data){
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

function initGroups(jquery){
    id = "#group_name"
    displayField = 'name'
    filter_ids = null
    auto_complete(id, url, displayField, filter_ids);
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
    //add category drop down functionality
    category_id = "category"
    sector_id = "sector"
    category_get(category_id=category_id, sector_id=sector_id);
    //add name autocomplete
    url = '/provider/list/autocomplete'
    id = "#provider_name"
    filter_ids = ['sector', 'category', 'location', 'manual_location']
    auto_complete(id, url, 'name', filter_ids);
    //add location field toggles 
    toCheck = document.getElementById("location")
    checkValue = "manual"
    toBeVisibleID = "manual_location_div"
    toCheck.addEventListener("input", function(){
        toggle_fields(toCheck, checkValue, toBeHiddenID=null, toBeVisibleID=toBeVisibleID);
    });
    toCheck.addEventListener("input", function(){
        request_location(toCheck, "gps");
    });
    // viewMap();
    // view results on map
    listView = document.getElementById("businessList");
    listLink = document.getElementById("viewList");
    mapView = document.getElementById("mapView");
    mapLink = document.getElementById("viewOnMap")
    mapContainer = document.getElementById("viewDiv")
    mapLink.addEventListener("click", function(){
        // viewMap();
        // let params = ['sector', 'category', 'name', 'reviewed_filter',
        //               'friends_filter', 'groups_filter', 'sort', 'page'];
        // let query_args = {};
        // urlParams = new URLSearchParams(window.location.search);
        // for (let param of params){
        //     query_args[param] = urlParams.get(param);
        // }
        // let url = "/provider/search/json";
        listView.hidden = true;
        mapView.hidden = false;
        if(mapContainer.childElementCount == 0){
            viewMap(searchHome, searchResults);

        }
    });
    listLink.addEventListener("click", function(){
        listView.hidden = false;
        mapView.hidden = true;
    });


}

function viewMap(location, searchResults){
    require(["esri/Map",
             "esri/views/MapView",
             "esri/layers/FeatureLayer",
             "esri/Graphic"],
              function(Map, MapView, FeatureLayer, Graphic) {
                var map = new Map({
                    basemap: "streets-navigation-vector"
                });
  
                var view = new MapView({
                    container: "viewDiv",
                    map: map,
                    center: [location.longitude, location.latitude], // longitude, latitude
                    zoom: 10
                });

                var homeMarker = [new Graphic({
                    attributes: {
                        ObjectID: 1,
                        address: location.address
                    },
                    geometry: {
                        type: "point",
                        longitude: location.longitude,
                        latitude: location.latitude
                    }
                })];
                var featureLayer = new FeatureLayer({
                    source: homeMarker,
                    renderer: {
                        type: "simple",                    // autocasts as new SimpleRenderer()
                        symbol: {                          // autocasts as new SimpleMarkerSymbol()
                            type: "simple-marker",
                            color: [56, 168, 0, 1],
                            outline: {                       // autocasts as new SimpleLineSymbol()
                                style: "none",
                                color: [255, 255, 255, 0],
                            },
                            size: 8
                        }
                    },
                    objectIdField: "ObjectID",           // This must be defined when creating a layer from `Graphic` objects
                    fields: [
                        {
                            name: "ObjectID",
                            alias: "ObjectID",
                            type: "oid"
                        },
                        {
                            name: "address",
                            alias: "address",
                            type: "string"
                        }
                    ]
                });
                map.layers.add(featureLayer);
                createBusinessLayer(searchResults,map);
    });
}
//create graphics and add to feature layer
function createBusinessLayer(searchResults, map){
    require(["esri/layers/FeatureLayer","esri/Graphic"],
            function(FeatureLayer, Graphic){
            var markers = searchResults.map(function(biz){
                return new Graphic({
                    attributes: {
                        ObjectID: biz.id,
                        nameLink: `<a href=` + `${document.getElementById(`${biz.name}-${biz.id}-link`).href}` + `>${biz.name}</a>`,
                        name : biz.name,
                        categories: biz.categories.replace(",", ", "),
                        telephone: `(${biz.telephone.slice(0,3)}) ${biz.telephone.slice(3,6)}-${biz.telephone.slice(6,)}`,
                        email: biz.email,
                        address: `${biz.line1} \n ${biz.city}, ${biz.state_short}`, 
                        rating: `${(biz.reviewAverage==null) ? 'N/A' : biz.reviewAverage}`,
                        cost: `${(biz.reviewCost==null) ? 'N/A' : biz.reviewCost}`,
                        count: biz.reviewCount
                    },
                    geometry: {
                        type: "point",
                        longitude: biz.longitude,
                        latitude: biz.latitude
                    }
                });
            });

            var businessPopUp = {
                "title": "Business Profile",
                "content": [{
                    "title": "{name}",
                    "type": "fields",
                    "fieldInfos": [
                        {
                            "fieldName": "nameLink",
                            "label": "Name",
                        },
                        {
                            "fieldName": "categories",
                            "label": "Categories",
                        },
                        {
                            "fieldName": "address",
                            "label": "Address",
                        },
                        {
                            "fieldName": "telephone",
                            "label": "Telephone",
                        },
                        {
                            "fieldName": "rating",
                            "label": "Avg. Rating",
                        },
                        {
                            "fieldName": "cost",
                            "label": "Avg. cost",
                        },
                        {
                            "fieldName": "count",
                            "label": "# Reviews",
                        },                                                 
                    ]
                }]
            };

            var businessLabels = {
                // autocasts as new LabelClass()
                symbol: {
                    type: "text",
                    color: [0,0,0,255],  // black
                    font: { family: "sans-serif", size: 10, weight: "normal" }
                },
                labelPlacement: "center-right",
                labelExpressionInfo: {
                  expression: "$feature.name"
                }
            };

            var featureLayer = new FeatureLayer({
                source: markers,
                renderer: {
                    type: "simple",                    // autocasts as new SimpleRenderer()
                    symbol: {                          // autocasts as new SimpleMarkerSymbol()
                        type: "simple-marker",
                        color: [255,0,0],
                        outline: {                       // autocasts as new SimpleLineSymbol()
                            style: "none",
                            color: [255, 255, 255, 0]
                        },
                        size: 8
                    }
                },
                objectIdField: "ObjectID",           // This must be defined when creating a layer from `Graphic` objects
                fields: [
                    {
                        name: "ObjectID",
                        alias: "ObjectID",
                        type: "oid"
                    },
                    {
                        name: "address",
                        alias: "address",
                        type: "string"
                    },
                    {
                        name: "nameLink",
                        alias: "nameLink",
                        type: "string"
                    },                    
                    {
                        name: "name",
                        alias: "name",
                        type: "string"
                    },
                    {
                        name: "categories",
                        alias: "categories",
                        type: "string"
                    },
                    {
                        name: "telephone",
                        alias: "telephone",
                        type: "string"
                    },
                    {
                        name: "rating",
                        alias: "rating",
                        type: "string"
                    },
                    {
                        name: "cost",
                        alias: "cost",
                        type: "string"               
                    },
                    {
                        name: "count",
                        alias: "count",
                        type: "integer"               
                    }
                ],
                popupTemplate: businessPopUp,
                labelingInfo: [businessLabels]
            });
            map.layers.add(featureLayer)
    });

}
//JS for provider add form
function initProviderAdd(jquery){
    category_get(category_id="category", sector_id="sector")
    //select unknown, line1, line2, zip
    toCheck = document.getElementById("addressUnknown");
    toBeHiddenID = ["address-line1", "address-line2", "address-zip"]
    toBeVisibleID="toggle_message"
    checkValue = true
    toCheck.addEventListener("input", function(){
        toggle_fields(toCheck, checkValue, toBeHiddenID, toBeVisibleID);
        toggle_fields_required(toCheck, checkValue, toBeHiddenID)
    });

}


//execute when DOM loaded
$(document).ready(function(){
    if( $("#submit-register").length){
        $(document).ready(initRegister);

    } else if ( $("#review_form").length){
        $(document).ready(initReview);

    } else if ($("#groupSearch").length){
        $(document).ready(initGroups);
    } else if ($("#friendadd").length){
        $(document).ready(initFriends);
    } else if ($("#providersearch").length){
        $(document).ready(initSearch);
    } else if ($("#provideraddform").length){
        $(document).ready(initProviderAdd);
    } 
});