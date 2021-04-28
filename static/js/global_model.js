var globalModel = globalModel || {};

var parseCollection = function (response) {
    var result = response.collection;
    return result;
};

//------------------------------------------------
// TYPY DÁT
//------------------------------------------------
var KategoriaModel = Backbone.Model.extend({
    defaults: {
        id:              '',
        kategoria_nazov: ''    /* <-- názov kategórie */
    },
    url: "/kategorie"
});

var ProduktModel = Backbone.Model.extend({
    defaults: {
        id:              '',
        kategoria_id:    '',   /* <-- väzba na kategóriu  */
        produkt_nazov:   '',   /* <-- názov produktu      */
        produkt_popis:   '',   /* <-- popis produktu      */
        produkt_obrazok: '',   /* <-- názov súboru obrázku*/
        produkt_cena:    ''    /* <-- cena v EUR */
    },
    url: "/produkty"
});

var KosikModel = Backbone.Model.extend({
    defaults: {
        id:          '', /* <-- väzba na produkt */
        kosik_pocet: ''  /* <-- aký počet daného produktu je v košíku*/
    }
});

var ObrazkyModel = Backbone.Model.extend({
    defaults: {
        id:                 '',
        kategoria_id:       '',
        produkt_obrazok:    '',
        produkt_nazov:      ''
    }
});
var GaleriaModel = Backbone.Model.extend({
    defaults:{
        id:                 '',
        produkt_obrazok:    '',
        produkt_id:         '',
        hlavny_obrazok:     ''
    }
});

//------------------------------------------------
// VYTVORIME TYPY ZOZNAMOV (TYPY KOLEKCII)
//------------------------------------------------

var KategoriaZoznam = Backbone.Collection.extend({    
    model: KategoriaModel,
    url: "/kategorie",
    parse: parseCollection
});

var ProduktZoznam = Backbone.Collection.extend({
    model: ProduktModel,
    url: "/produkty",
    parse: parseCollection
});

var KosikZoznam = Backbone.Collection.extend({
    model: KosikModel,
    url: "/obsahkosik",
    parse: parseCollection
});

var ObrazkyZoznam = Backbone.Collection.extend({
    model: ObrazkyModel,
    url: "/obrazkyzoznam",
    parse: parseCollection
});

var GaleriaZoznam = Backbone.Collection.extend({
    model: GaleriaModel,
    url: "/produktygaleria",
    parse: parseCollection
});

var globalModel = {
    //---------------------------------------
    // VYTVORIME OBJEKTY V NAMESPACE
    //---------------------------------------    
    kategoriaZoznam : new KategoriaZoznam([]),
    produktZoznam   : new ProduktZoznam  ([]),
    kosikZoznam     : new KosikZoznam    ([]),
    obrazkyZoznam   : new ObrazkyZoznam  ([]),
    galeriaZoznam   : new GaleriaZoznam  ([]),
    getURLParameter : function (sParam) {
        var sPageURL = window.location.pathname;
        var sURLVariables = sPageURL.split('/');
        return sURLVariables[sURLVariables.length - 1];
    }
}

var jeNacitanyGlobalModel = false;

$(document).ready(function() {

    if (jeNacitanyGlobalModel) {
        console.log('>>> Tento súbor už bol načítaný! (GlobalModel)');
        return;
    }

    jeNacitanyGlobalModel = true;

    //------------------------------------------------
    // VLOZIME DO ZOZNAMOV NEJAKE TESTOVACIE UDAJE
    //------------------------------------------------

    globalModel.kategoriaZoznam = new KategoriaZoznam([]);
    globalModel.produktZoznam   = new ProduktZoznam([]);

    globalModel.kosikZoznam = new KosikZoznam([
     new KosikModel({ id: '01', kosik_pocet: '1' }),
     new KosikModel({ id: '02', kosik_pocet: '3' }),
     new KosikModel({ id: '03', kosik_pocet: '1' }),
     new KosikModel({ id: '04', kosik_pocet: '2' })
    ]);

});
