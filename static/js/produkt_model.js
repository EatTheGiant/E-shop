

var vlozDoKosika = function (produkt_id) {
    var obr_id  = $("#expandedImg").attr('data-obr-id');
    console.log("obr id " + obr_id);
      $.ajax({
        type: "PUT",
        url:  "/kosik/" + produkt_id,
        data: JSON.stringify({'message': "OK", 'obrazok': obr_id}, null, '\t'),
        dataType: "json",
        contentType: "application/json;charset=UTF-8",
        timeout: 993500,
        success: function() {
            location.href="/prehlad";
        },
        error: function (jqXHR, textStatus, errorThrown) { console.log(">>> vlozDoKosika Chyba!"); }
    });
};

//---------------
// BACKBONE VIEWS
//---------------
var ProduktDetailView = Backbone.View.extend({
    el: '#produkt-detail',
    initialize: function () {
        this.render();
    },
    render: function () {
        this.$el.html('');
        var _id = globalModel.getURLParameter('id');
        var produktDetail = globalModel.produktZoznam.get(_id);
        if (produktDetail == null) {
            // this.$el.append(' <h2> Nenašiel sa produkt s id = "' + _id + '" ! </h2> ');
        } else {

            var url = window.location.href;
            var pathid = new URL(url).pathname.split('/');
            z = 0;
            var hlavnyObrazok = '';

            globalModel.galeriaZoznam.each(function (model) {
                if (model.get('produkt_id') == pathid[2] && model.get('hlavny_obrazok') == 1){
                    hlavnyObrazok = '<img src="../static/img/velke/'+ model.get('produkt_obrazok') + '" id="expandedImg" data-obr-id="'+ model.get('id') +'" class="col s12 materialboxed responsive-img">';
                    z++;
                }
            });


            this.$el.append(
                '<div id="hlav_obr" class="col s12 m6">' + hlavnyObrazok + '</div>' +
                '<div class="col s12 m6">' +
                '   <div class="row"> ' +
                '       <div class="col s12"> <h3 id="produkt-title">' + produktDetail.get('produkt_nazov') + '</h3> </div>' +
                '       <div class="col s12"> <p id="produkt-text"> ' + produktDetail.get('produkt_popis') + ' </p> </div>' +
                '       <div class="col s12"> <h4 id="produkt-cena"> Cena: ' + Number(produktDetail.get('produkt_cena')).toFixed(2) + '&nbsp;€  </h4> </div>' +
                '       <div class="col s12"> <button id="produkt-potvrd" onclick="vlozDoKosika(' + _id + ')" class="waves-effect waves-light btn">Pridaj do košíka</button> </div>' +
                '   </div> ' +
                '</div>'
            );
        }
        return this;
    }
});

var GaleriaObrazkyView = Backbone.View.extend({
    el: '#galeria_obrazky',
    initialize: function () {
        this.render();
    },
    render: function () {
        this.$el.html('');
        var url2 = window.location.href ;
        var pathid2 = new URL(url2).pathname.split('/');
        var z2=0;
        var html_content = "";

        globalModel.galeriaZoznam.each(function (model) {
            if (model.get('produkt_id') == pathid2[2]) {
                z2++;
                html_content +=
                    '<div class="card col s12 m4 l3 xl2 hoverable" style="height: 250px; width: 200px;" > ' +
                    '  <div class="card-image waves-effect waves-block waves-light"> ' +
                    '       <img class="col s12" src="../static/img/velke/' + model.get('produkt_obrazok') + '" ' +
                    '        id="pic' + z2 + '" ' +
                    '        onclick="openImg(this)" ' +
                    '        data-obr-id="'+ model.get('id') + '">' +
                    '  </div> ' +
                    '</div> ';
                console.log(model.get('id'));
            }
        });
        this.$el.append(
            html_content
        );
        return this;    
    }
});

var produktDetailView = new ProduktDetailView;
var galeriaObrazkyView = new GaleriaObrazkyView;

var jeNacitanyProduktModel = false;

$(document).ready(function() {

    if (jeNacitanyProduktModel) {
        console.log('>>> Tento súbor už bol načítaný! (ProduktModel)');
        return;
    }

    $.when(
        globalModel.produktZoznam.fetch(),
        globalModel.galeriaZoznam.fetch()
    ).then(function () {
                
        $.when(
            produktDetailView.render(),
            galeriaObrazkyView.render()
        ).then(function () {
            //$('.materialboxed').materialbox({
            //    inDuration:275,
            //    outDuration:200
            //});
            jeNacitanyProduktModel = true;
        });        
    
    });

});
