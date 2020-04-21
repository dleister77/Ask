const MessageRow = {
  props: ['message'],
  template: `
          <tr
            :style="!message.read ? 'font-weight:bold' : ''"
            class="d-flex flex-wrap border-bottom">
              <td class="d-none d-md-block col-1 order-md-1 folder-row">
                  <input
                  class="select"
                  type="checkbox"
                  v-bind:value="message.id"
                  v-on:change="updateList('selected-messages', [$event.target.checked, $event.target.value])">
                  </td>
              <td class="inbox_id folder-row" hidden>{{message.id}}</td>
              <td v-on:click="$emit('show-message')" class="col-8 col-md-2 order-1 order-md-2 folder-row">{{message.sender_full_name}}</td>
              <td
                @click="$emit('show-message')"
                class="col-12 col-md-2 folder-row order-3 order-md-3">{{message.subject}}</td>
              <td v-on:click="$emit('show-message')" class="order-4 col-12 col-md-6 folder-message-body folder-row">{{message.body}}</td>
              <td v-on:click="$emit('show-message')" class="order-2 order-md-4 col-4 col-md-1 folder-row">{{localize_time}}</td>
          </tr>`,
  computed: {
    localize_time() {
      const now = new Date();
      const msgTime = new Date(this.message.timestamp);
      if (msgTime.toDateString() === now.toDateString()) {
        return msgTime.toLocaleString('en-us', { timeStyle: 'short' });
      } return msgTime.toLocaleString('en-us', { dateStyle: 'medium' });
    },
  },
  methods: {
    updateValue(value) {
      this.$emit('input', value);
    },
    updateList(message, value) {
      this.$emit(message, value);
    },
  },
};

export default MessageRow;
