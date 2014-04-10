/* global define */

define([
    'backbone',
    '../utils'
], function(Backbone, utils) {

    var AnalysisModel = Backbone.Model.extend({
        urlRoot: function() {
            return utils.toAbsolutePath('api/analyses/');
        }
    });

    var AnalysisCollection = Backbone.Collection.extend({
        url: function() {
            return utils.toAbsolutePath('api/analyses/');
        },

        model: AnalysisModel
    });

    var AssessmentModel = Backbone.Model.extend({
        urlRoot: function() {
            return utils.toAbsolutePath('api/assessments/');
        }
    });

    var AssessmentCollection = Backbone.Collection.extend({
        url: function() {
            return utils.toAbsolutePath(
                'api/analyses/' + this.analysisId + '/assessments/');
        }
    });

    return {
        AnalysisModel: AnalysisModel,
        AnalysisCollection: AnalysisCollection,
        AssessmentModel: AssessmentModel,
        AssessmentCollection: AssessmentCollection
    };

});
