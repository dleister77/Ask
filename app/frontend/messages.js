/**
 * User to user messages
 * @constructor
 * @property {Array} list - list of messages
 * @property {Number} index - index of active message
 * @property {Object} active - active message from list
 * @property {Array} selected_ids - list of selected messages from list
 * @property {Html Collection} folder_rows - message rows from folder table view
 * @property {String} read_url - url used to notify db when message is read
 * @property {String} move_url - url used to move message within db.
 * @method mark_as_read - updates list and db when message is read
 * @method format_read - reformats folder table rows when message is read
 * @method move - moves selected messages to specified folders
 * @method reset_active - resets active message info when back at folder view
 * @method next - loads next message to read
 * @method previous - loads preview message to read 
 */
function Messages(list) {
    this.list = list,
    this.index = null,
    this.active = null,
    this.selected_ids = [],
    this.folder_rows = [],
    this.read_url = null,
    this.move_url = null,
    this.mark_as_read = mark_as_read,
    this.format_read = format_read,
    this.move = move_messages,
    this.reset_active = reset_active_message,
    this.next = read_next,
    this.previous = read_previous
}

function mark_as_read(message_id=this.active.id){
    let parameters = {
        url: this.read_url,
        type: "POST",
        data: {id: message_id},
        dataType: "json",
        context: this,
    };
    addcsrf();
    $.ajax(parameters).done(function(data){
        if (data['status'] == "success"){
            messages.list.find( ({id}) => id == this.active.id).read = true;
            for (row of this.folder_rows) {
                if (row.getElementsByClassName("inbox_id")[0].innerHTML == message_id){
                    for (let child of row.children){
                        child.classList.remove("message_unread");
                    }
                    break;
                }
            }
        } else if (data['status'] == "failure") {
            console.log("failed to update message as read");
        }
    });
}

function format_read(){
    for (let row of this.folder_rows){
        let row_id = row.getElementsByClassName("inbox_id")[0].innerHTML;
        read = (this.list.find(({id}) => id == row_id)).read;
        if (!read){
            for (let child of row.children){
                child.classList.add("message_unread");
            }
        }
    }
}

function move_messages(status){
    let form_data = {'message_id': this.selected_ids.toString(),
                    'status': status};
    post(this.move_url, form_data);
}

function reset_active_message(){
    this.index = null;
    this.active = null;
    this.selected_ids = [];    
}

function read_previous(){
    if (this.index > 0){
        this.index -= 1;
        this.active = this.list[this.index];
        load_message_read(this.active);
        this.mark_as_read();
    }
}

function read_next(){
    if (this.index < this.list.length){
        this.index += 1;
        this.active = this.list[this.index];
        load_message_read(this.active);
        this.mark_as_read();
    }
}

function load_message_read(message) {
    document.getElementById("read_sender").innerHTML = `From: ${message.sender_full_name}`;
    document.getElementById("read_timestamp").innerHTML = message.timestamp;
    document.getElementById("read_subject").innerHTML = `Subject: ${message.subject}`
    document.getElementById("read_body").innerHTML = message.body;
}

function localize_inbox_datetimes(inbox_rows){
    let now = new Date()
    for (let row of inbox_rows){
        let element = row.getElementsByClassName("inbox_timestamp")[0]
        let row_date = new Date(row.getElementsByClassName("inbox_timestamp")[0].innerHTML)
        if (row_date.toDateString() == now.toDateString()){
            element.innerHTML = row_date.toLocaleString('en-us', {timeStyle: "short"})
        } else{
            element.innerHTML = row_date.toLocaleString('en-us', {dateStyle: "medium"})
        }
    }
}

function select_all_rows(select_all){
    for (let row of messages.folder_rows){
        row.querySelector(".select").checked = select_all.checked;
    }
}

function update_active_ids(row){
    let cell = row.getElementsByClassName("inbox_id")[0]
    let id = cell.innerHTML;
    if (row.getElementsByTagName('input')[0].checked){
        messages.selected_ids.push(id);
    } else if (messages.selected_ids.includes(id)){
        messages.selected_ids = messages.selected_ids.filter( (element) => element != id);
    }
}

function reply_to_message(event){
    document.getElementById("msg_new_recipient_id").value = messages.active.sender_id;
    document.getElementById("msg_new_conversation_id").value = messages.active.conversation_id
    document.getElementById("msg_new_recipient").value = messages.active.sender_full_name;
    if (messages.active.subject.startsWith("Re:")){
        document.getElementById("msg_new_subject").value = messages.active.subject
    } else {
    document.getElementById("msg_new_subject").value = `Re: ${messages.active.subject}`
    }
    document.getElementById("msg_new_body").value = 
            `\n\nOn ${messages.active.timestamp}, ${messages.active.sender_full_name} wrote:\n  ${messages.active.body}`;
    page.navigate_next('message_send');
}

function autocomplete_recipient_name(){
    let url = '{{ url_for("main.get_friends") }}';
    let selector_id = "#msg_new_recipient";
    let label_fields = ['full_name'];
    let value_field = "full_name";
    let value_field_id = "#msg_new_recipient_id"
    let filter_ids = [];
    let submit_id = "submit_msg";
    let validation_message = "Please choose a name from the list.";
    autocomplete_by_id(selector_id, url, label_fields, value_field, 
                    value_field_id, filter_ids, submit_id,
                    validation_message);
}


