/* global define */

define([
    'marionette',
    'cilantro'
], function(Marionette) {

    var AnalysisItem = Marionette.ItemView.extend({
        className: 'row-fluid',

        template: 'varify/analysis/item'
    });

    return {
        AnalysisItem: AnalysisItem
    };

});
