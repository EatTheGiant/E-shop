var ObrazkyZoznamView = Backbone.View.extend({
    el: '#gallery-zoznam',
    initialize: function () {
        this.render();
    },
    render: function () {
        this.$el.html('')
        var _id = [];
        var url = window.location.href ;
        var pathid = new URL(url).pathname.split('/');
        for(var y=0; y<16; y++){
            _id[y] = Math.floor(Math.random() * globalModel.obrazkyZoznam.length) + 1;
            if(pathid[2] == _id[y]){
                _id[y] = Math.floor(Math.random() * globalModel.obrazkyZoznam.length) + 1;
                if(pathid[2] == _id[y]){
                    _id[y] = Math.floor(Math.random() * globalModel.obrazkyZoznam.length) + 1;
                }
            }
        }
        var uniqueItems = Array.from(new Set(_id));
        
        for(var i=1; i<=4; i++){
              
                var obrazkyDetail = globalModel.obrazkyZoznam.get(uniqueItems[i]);
                if (!(_.isNull(obrazkyDetail) || _.isNaN(obrazkyDetail) || _.isUndefined(obrazkyDetail))){ 
                this.$el.append(
                    '<div class="card col s11 m4 l2 xl1 offset-l1 hoverable" style="height: 180px; width:150px;"> ' +
                    '  <div class="card-image waves-effect waves-block waves-light"> ' +
                    '    <a href="/produkt/' + obrazkyDetail.get('id') + '"> ' +
                    '       <img class="col s12" src="../static/img/velke/' + obrazkyDetail.get('produkt_obrazok') + '" ' +
                    '        alt="' + obrazkyDetail.get('produkt_nazov') + '" ' +
                    '        id="main_pic" ' +
                    '        onclick="myFunction(this);" >' +
                    '    </a> ' +
                    '  </div> ' +
                    '</div> '
                );
            }
        }
        return this;
    }
});
var obrazkyZoznamView = new ObrazkyZoznamView;

$(document).ready(function() {

    $.when(
        globalModel.obrazkyZoznam.fetch()
    ).then(function () {
        obrazkyZoznamView.render();
    });
});
