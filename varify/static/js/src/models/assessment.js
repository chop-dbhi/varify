/* global define */

define([
    'underscore',
    'backbone',
    '../utils'
], function(_, Backbone, utils) {

    var Assessment = Backbone.Model.extend({
        urlRoot: function() {
            return utils.toAbsolutePath('api/assessments/');
        },

        defaults: {
            'evidence_details': '',
            'sanger_requested': 'undefined',
            'assessment_category': 1,
            'father_result': 'undefined',
            'mother_result': 'undefined',
            'pathogenicity': 1,
            'created': 'undefined',
            'modified': 'undefined',
            'sample_result': 'undefined'
        },

        parse: function(response) {
            if (response !== null) {
                var data = response;

                var objFields = [
                    'assessment_category',
                    'father_result',
                    'mother_result',
                    'pathogenicity'
                ];

                _.each(objFields, function(field) {
                    if (response[field]) {
                        data[field] = response[field].id;
                    }
                });

                return data;
            }
        }
    });

    var AssessmentMetrics = Backbone.Model.extend({
        url: function() {
            return '' + utils.getRootUrl() + 'api/variants/' +
                   this.variantId + '/assessment-metrics/';
        },

        initialize: function(attrs, options) {
            if (!(this.variantId = options.variantId)) {
                throw new Error("Variant ID required");
            }
        }
    });

    return {
        Assessment: Assessment,
        AssessmentMetrics: AssessmentMetrics
    };
});
