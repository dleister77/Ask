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
            <dl class="row">
              <dt class="d-none d-md-block col-md-2">From</dt>
              <dd class="col-12 col-md-10 message-read">{{ message.sender_full_name }} </dd>

              <dt class="d-none d-md-block col-md-2">Subject</dt>
              <dd class="col-12 col-md-10 message-read">{{ message.subject }}</dd>
            </dl>
          </div>
          <div class="col-4">
              <p class="message-read">{{ localize_time() }}</p>
          </div>
      </div>
      <br>
      <div class="row">
          <div class="col-12">
              <p class="message-read text-responsive" id="message-read-body">{{ message.body }}</p>
          </div>
      </div>
  </div>`,
};

export default MessageRead;
