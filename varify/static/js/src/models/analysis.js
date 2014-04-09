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
        model: AnalysisModel
    });

    return {
        AnalysisModel: AnalysisModel,
        AnalysisCollection: AnalysisCollection
    };

});
