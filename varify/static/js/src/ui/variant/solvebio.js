/* global define */

define([
    'cilantro',
    'marionette'
], function(c, Marionette) {

    var EmptyClinvarItem = c.ui.EmptyView.extend({
        className: 'muted',

        icon: '',

        align: 'left'
    });

    var ClinvarItem = Marionette.ItemView.extend({
        tagName: 'li',

        template: 'varify/variant/clinvar-item'
    });

    var Clinvar = Marionette.CompositeView.extend({
        template: 'varify/variant/clinvar',

        itemView: ClinvarItem,

        itemViewContainer: '[data-target=items]',

        emptyView: EmptyClinvarItem
    });

    return {
        Clinvar: Clinvar
    };

});
