/* global define */

define([
    'marionette'
], function(Marionette) {

    var EmptyGene = Marionette.ItemView.extend({
        template: 'varify/tables/row/genes/empty'
    });

    var GeneItem = Marionette.ItemView.extend({
        template: 'varify/tables/row/genes/item'
    });

    var GeneList = Marionette.CollectionView.extend({
        itemView: GeneItem,

        emptyView: EmptyGene
    });

    return {
        EmptyGene: EmptyGene,
        GeneItem: GeneItem,
        GeneList: GeneList
    };

});
