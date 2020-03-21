let message_row = {
    props:['message'],
    template: `
            <tr v-bind:style="!message.read ? 'font-weight:bold' : ''" class="d-flex">
                <td class="d-none d-md-block col-1">
                    <input
                    class="select"
                    type="checkbox"
                    v-bind:value="message.id"
                    v-on:change="updateList('selected-messages', [$event.target.checked, $event.target.value])">
                    </td>
                <td class="inbox_id" hidden>{{message.id}}</td>
                <td v-on:click="$emit('show-message')" class="col-2">{{message.sender_full_name}}</td>
                <td v-on:click="$emit('show-message')" class="col-2">{{message.subject}}</td>
                <td v-on:click="$emit('show-message')" class="col-6 folder-message-body">{{message.body}}</td>
                <td v-on:click="$emit('show-message')" class="col-1">{{localize_time}}</td>
            </tr>`,
    computed: {
        localize_time: function(){
            let now = new Date();
            let msg_time = new Date(this.message.timestamp);
            if (msg_time.toDateString() == now.toDateString()){
                return msg_time.toLocaleString('en-us', {timeStyle: "short"})
            } else {
                return msg_time.toLocaleString('en-us', {dateStyle: "medium"})
            }
        }
    },
    methods: {
        updateValue: function(value){
            this.$emit('input', value);
        },
        updateList: function(message,value){
            this.$emit(message, value);
        }
    },
};

export default message_row;