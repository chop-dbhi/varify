define [
    'underscore'
    'backbone'
    '../utils'
], (_, Backbone, util) ->


    class AssessmentMetrics extends Backbone.Model
        url: ->
            "#{ util.getRootUrl() }api/variants/#{ @variant_id }/assessment-metrics"

        initialize: (attrs, options) ->
            if not (@result = options.result_id)
                throw new Error "Result ID required"
            if not (@variant_id = options.variant_id)
                throw new Error "Variand ID required"


    { AssessmentMetrics }
