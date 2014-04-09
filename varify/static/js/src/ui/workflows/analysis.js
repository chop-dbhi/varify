/* global define */

define([
    'cilantro',
    'marionette',
    '../analysis',
    '../../models'
], function(c, Marionette, analysis, models) {

    var AnalysisWorkflow = Marionette.Layout.extend({
        className: 'analysis-workflow',

        template: 'varify/workflows/analysis',

        regions: {
            analyses: '.analyses-region'
        },

        regionViews: {
            analyses: analysis.AnalysisList
        },

        initialize: function() {
            // When this workflow is loaded, toggle shared components
            this.on('router:load', function() {
                // Fully hide the panel; do not leave an edge to show/hide
                c.panels.context.closePanel({full: true});
                c.panels.concept.closePanel({full: true});
            });
        },

        onRender: function() {
            this.analyses.show(new this.regionViews.analyses({
                collection: new models.AnalysisCollection()
            }));
        }
    });

    return {
        AnalysisWorkflow: AnalysisWorkflow
    };

});
