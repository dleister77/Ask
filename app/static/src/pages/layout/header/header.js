import Vue from 'vue';
import axios from 'axios';


const topNavbar = new Vue({
    el: '#topNavbar',
    data: {
        unreadCount: initial_unread_count,
        unready_url: unread_url,
    },
    delimiters: ['[[',']]'],
    methods: {
        setUpTimer: function(){
            let intervalID = setInterval(this.getUnread, 60000)
        },
        getUnread: function(url){
            let self = this;
            axios.get(this.unread_url)
                .then(function(response){
                    self.unreadCount = response.data.unread_count;
                })
                .catch(function(error){
                    console.log(error);
                })
        }
        
    },
    created: function(){
        this.setUpTimer();
    }
});