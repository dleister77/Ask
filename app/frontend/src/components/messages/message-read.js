const MessageRead = {
  props: {
    message: Object,
  },
  methods: {
    localize_time() {
      const time = new Date(this.message.timestamp);
      return time.toLocaleString('en-us', { dateStyle: 'long', timeStyle: 'short' });
    },
  },
  template: `
  <div id="message-read">
      <div class="row justify-content-between border-bottom border-top py-3"
       id="message-read-header">
          <div class="col-8">
              <p class="message-read">From: {{ message.sender_full_name }} </p>
              <p class="message-read">Subject: {{ message.subject }}</p>
          </div>
          <div class="col-4">
              <p class="message-read">{{ localize_time() }}</p>
          </div>
      </div>
      <br>
      <div class="row">
          <div class="col-12">
              <p class="message-read" id="message-read-body">{{ message.body }}</p>
          </div>
      </div>
  </div>`,
};

export default MessageRead;
