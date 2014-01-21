define [
    'underscore'
    'backbone'
    '../utils'
], (_, Backbone, utils) ->


    class Phenotype extends Backbone.Model
        urlRoot: ->
            utils.toAbsolutePath('api/samples/#{ @sample_id }/phenotype/')

    { Phenotype }
