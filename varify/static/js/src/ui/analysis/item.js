/* global define */

define([
    'marionette',
    'cilantro'
], function(Marionette) {

    var AnalysisItem = Marionette.ItemView.extend({
        className: 'row-fluid',

        template: 'varify/analysis/item',

        modelEvents: {
            sync: 'render'
        }
    });

    return {
        AnalysisItem: AnalysisItem
    };

});
