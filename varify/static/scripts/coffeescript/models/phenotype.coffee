define [
    'underscore'
    'backbone'
    '../utils'
], (_, Backbone, utils) ->


    class Phenotype extends Backbone.Model
        urlRoot: ->
            sample_id = @get('sample_id')
            utils.toAbsolutePath("api/samples/#{ sample_id }/phenotypes/")
            
        lowestPriority: 10
        highestPriority: 1
        
        
    { Phenotype }
