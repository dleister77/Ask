import Vue from 'vue';


const groupProfile = new Vue({
  el: '#appContent',
  delimiters: ['[[', ']]'],
  mounted() {
    $('[data-toggle="tooltip"]').tooltip();
  },
});

export default groupProfile;
