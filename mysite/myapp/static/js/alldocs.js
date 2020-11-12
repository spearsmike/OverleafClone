  var app5 = new Vue({
    el: '#myapp',
    data: {
        documents: [],
        seen:true,
        unseen:false
      },
      //Adapted from https://stackoverflow.com/questions/36572540/vue-js-auto-reload-refresh-data-with-timer
      created: function() {
            this.fetchDocumentList();
            this.timer = setInterval(this.fetchDocumentList, 10000);
      },
      methods: {
        fetchDocumentList: function() {
            // $.get('/', function(suggest_list) {
            //     this.documents = suggest_list.documents;
            //     console.log(suggest_list);
            // }.bind(this));
            axios
              .get('/documents/all')
              // .then(response => console.log(response.data))
              .then(response => (this.documents = response.data.documents))
            console.log(this.documents)
            this.seen=false
            this.unseen=true
        },
        cancelAutoUpdate: function() { clearInterval(this.timer) }
      },
      beforeDestroy() {
        // clearInterval(this.timer)
        this.cancelAutoUpdate();
      }
  })