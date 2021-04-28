//---------------
// BACKBONE VIEWS
//---------------

var kategoriaFilter = -1;

var KategoriaZoznamView = Backbone.View.extend({
    el: '#kategoria-filter',
    initialize: function () {
        this.render();
    },
    render: function () {
        this.$el.html('');
        this.$el.append('<a id="-1" href="#" class="collection-item kategoria-item">Všetky</a>');
        globalModel.kategoriaZoznam.each(function (model) {
            this.$el.append(
                  '<a id="'
                  + model.get('id') + '" href="#" class="collection-item kategoria-item '
                  + ((kategoriaFilter == parseInt(model.get('id'))) ? 'active' : '')
                  + ' ">' + model.get('kategoria_nazov')
                  + '</a>');
        }.bind(this));
        return this;
    }
});

var ProduktZoznamView = Backbone.View.extend({
    el: '#zoznam-produktov',
    initialize: function () {
        this.render();
    },
    render: function () {
        this.$el.html('');
        var filtrovanyZoznam = null;
        if (kategoriaFilter != -1) {
            filtrovanyZoznam = new ProduktZoznam(globalModel.produktZoznam.where({kategoria_id: kategoriaFilter}));
        } else {
            filtrovanyZoznam = globalModel.produktZoznam;
        }
        filtrovanyZoznam.each(function (model) {
            this.$el.append(
                '<div class="card small col s12 m6 l3 xl2 hoverable" > ' +
                '  <div class="card-image waves-effect waves-block waves-light"> ' +
                '    <a href="/produkt/' + model.get('id') + '"> ' +
                '       <img class="col s12" src="static/img/velke/' + model.get('produkt_obrazok') + '" > ' +
                '    </a> ' +
                '  </div> ' +
                '  <div class="card-content"> ' +
                '    <span class="card-title activator grey-text text-darken-4" style="white-space: nowrap;"> ' +
                        model.get('produkt_nazov') + '<br>' +
                        model.get('produkt_cena') + '&nbsp;€' +
                '       <i class="material-icons right">more_vert</i>' +
                '    </span> ' +
                '  </div> ' +
                '  <div class="card-reveal"> ' +
                '    <span class="card-title grey-text text-darken-4">' + model.get('produkt_nazov') + '<i class="material-icons right">close</i></span> ' +
                '    <p>' + model.get('produkt_popis') + '</p> ' +
                '  </div> ' +
                '</div> '
            );

        }.bind(this));
        return this;
    }
});

var kategoriaView = new KategoriaZoznamView;
var produktView = new ProduktZoznamView;

var updateFilter = function (kategoriaFilterArg) {
    kategoriaFilter = kategoriaFilterArg;

    $.when(
        kategoriaView.render(),
        produktView.render()
    ).then(function () {
        $('.kategoria-item').on('click',
            function() {
                var _id = $(this).attr("id");
                updateFilter(_id);
            }
        );
    });

};

var jeNacitanyPrehladModel = false;

$(document).ready(function() {

    if (jeNacitanyPrehladModel) {
        console.log('>>> Tento súbor už bol načítaný! (PrehladModel)');
        return;
    }

    $.when(
        globalModel.kategoriaZoznam.fetch(),
        globalModel.produktZoznam.fetch()
    ).then(function () {
        
        $.when(
            kategoriaView.render(),  // povodne katoria
            produktView.render()
        ).then(function () {
                $('.kategoria-item').on('click',
                    function() {
                        var _id = $(this).attr("id");
                        updateFilter(_id);
                    }
                );
            }
        )
    });
    
    jeNacitanyPrehladModel = true;

});
