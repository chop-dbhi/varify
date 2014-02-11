define [
    'underscore'
    'backbone'
    '../utils'
], (_, Backbone, utils) ->


    class Assessment extends Backbone.Model
        urlRoot: ->
            utils.toAbsolutePath('api/assessments/')

        defaults:
            'evidence_details': ''
            'sanger_requested': 'undefined'
            'assessment_category': 1
            'father_result': 'undefined'
            'mother_result': 'undefined'
            'pathogenicity': 1
            'created': 'undefined'
            'modified': 'undefined'
            'sample_result': 'undefined'

        parse: (response) ->
            if response?
                data = response

                objFields = ['assessment_category', 'father_result', 'mother_result', 'pathogenicity']

                _.each objFields, (field) ->
                    if response[field]
                        data[field] = (response[field])['id']

                return data


    class AssessmentMetrics extends Backbone.Model
        url: ->
            "#{ utils.getRootUrl() }api/variants/#{ @variant_id }/assessment-metrics/"

        initialize: (attrs, options) ->
            if not (@result = options.result_id)
                throw new Error "Result ID required"
            if not (@variant_id = options.variant_id)
                throw new Error "Variand ID required"


    { Assessment, AssessmentMetrics }
