/* global define */

define([
    'marionette',
    './item'
], function(Marionette, item) {

    var AnalysisList = Marionette.CompositeView.extend({
        itemView: item.AnalysisItem,

        itemViewContainer: '.items',

        template: 'varify/analysis/list'
    });

    return {
        AnalysisList: AnalysisList
    };

});
