
var onPlusMinusClick = function(_id, delta) {
    var kosikModel = globalModel.kosikZoznam.get(_id);
    if (kosikModel != null) {
        var n = Number(kosikModel.get('kosik_pocet'));
        n += delta;
        if (n < 1) {
            globalModel.kosikZoznam.remove(kosikModel);
        } else {
            kosikModel.set({ 'kosik_pocet': String(n) });
        }
        kosikView.render();
    }
    //alert('PLUS! ' + _id);
};

//---------------
// BACKBONE VIEWS
//---------------
var KosikZoznamView = Backbone.View.extend({
    el: '#zoznam-kosik',
    initialize: function () {
        this.render();
    },
    render: function () {
        this.$el.html('');
        celkovaCena = 0.0;
        globalModel.kosikZoznam.each(function (model) {
            var produktDetail = globalModel.produktZoznam.get(model.get('id'));
            var kosikCena     = Number(model.get('kosik_pocet')) * Number(produktDetail.get('produkt_cena'));
            celkovaCena      += kosikCena;
            this.$el.append(
                ' <tr class="produkt"> ' +
                '   <td><a class="kosik-zaznam" href="produkt.html?id=' + model.get('id') + '">' + produktDetail.get('produkt_nazov') + '</a></td> ' +
                '   <td><img src="static/img/velke/' + produktDetail.get('produkt_obrazok') + '" width="50" height="50" /></td> ' +
                '   <td class="cislo"> ' + kosikCena.toFixed(2) + '&nbsp;€ </td> ' +
                '   <td class="cislo"> ' + model.get('kosik_pocet') + ' </td> ' +
                '   <td> ' +
                '       <button id="MINUS-' + model.get('id') + '" class="button-small pure-button pocet-minus" onclick="onPlusMinusClick(&quot;' + model.get('id') + '&quot;, -1)">-</button> ' +
                '       <button id="PLUS-'  + model.get('id') + '" class="button-small pure-button pocet-plus" onclick="onPlusMinusClick(&quot;' + model.get('id') + '&quot;, +1)">+</button> ' +
                '   </td> ' +
                ' </tr> '
            );
        }.bind(produktDetail));
        // console.log('>>> celkovaCena:' + celkovaCena);
        $('#celkova-cena').html('');
        $('#celkova-cena').append('<strong>Celková cena: ' + celkovaCena.toFixed(2) + '&nbsp;€</strong>');
        
        return produktDetail;
    }
});

var kosikView = new KosikZoznamView;
var celkovaCena = 0.0;

var jeNacitanyKosikModel = false;

$(document).ready(function() {

    if (jeNacitanyKosikModel) {
        console.log('>>> Tento súbor už bol načítaný! (KosikModel)');
        return;
    }

    jeNacitanyKosikModel = true;

    var _id = globalModel.getURLParameter('id');
    if (_id != null) {
        var oldItem = globalModel.kosikZoznam.get(_id);
        if (oldItem != null) {
            var n = Number(oldItem.get('kosik_pocet'));
            n++;
            oldItem.set('kosik_pocet', String(n));
        } else {
            var newItem = new KosikModel({ id: _id, kosik_pocet: '1' });
            globalModel.kosikZoznam.add( [newItem] );
        }
    }

    kosikView.render();
    
    globalModel.kosikZoznam.each(
        function (obj) {
            var id    = obj.get('id');
            var pocet = obj.get('kosik_pocet');
            console.log('>>> id:' + id + '; pocet:' + pocet);
        }
    );

});
