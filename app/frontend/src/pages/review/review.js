import Vue from 'vue';


const review = new Vue({
    el: '#app',
    delimiters: ['[[', ']]'],
    data: {},
    methods: {
        setRequired: function(){
            let radio_choices = document.querySelectorAll("input[type='radio']");
            radio_choices.forEach(element => element.setAttribute("required", true));
        }
    },
    mounted: function(){
        this.setRequired();
    }
});

export default review;