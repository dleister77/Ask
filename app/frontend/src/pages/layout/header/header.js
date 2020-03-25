import Vue from 'vue';
import axios from 'axios';


const topNavbar = new Vue({
  el: '#topNavbar',
  data: {
    unreadCount: initial_unread_count,
    unread_url,
  },
  delimiters: ['[[', ']]'],
  methods: {
    setUpTimer() {
      setInterval(this.getUnread, 60000);
    },
    getUnread() {
      axios.get(this.unread_url)
        .then((response) => {
          this.unreadCount = response.data.unread_count;
        })
        .catch((error) => console.log(error));
    },
  },
  created() {
    this.setUpTimer();
  },
});
