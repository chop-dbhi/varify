define [
    'underscore'
    'backbone'
    '../utils'
], (_, Backbone, utils) ->


    class Result extends Backbone.Model
        url: ->
            "#{ utils.getRootUrl() }api/samples/variants/#{ @id }/"

        parse: (attrs) ->
            variant = attrs.variant

            # Bit of a hacked use of sortBy..
            variant.effects = _.sortBy variant.effects, (eff) ->
                utils.effectImpactPriority eff.impact

            uniqueGenes = {}
            genes = []

            _.each variant.effects, (eff) ->
                if not eff.transcript or not (gene = eff.transcript.gene)
                    return

                if /^LOC\d+/.test(gene.symbol) or uniqueGenes[gene.symbol]?
                    return

                uniqueGenes[gene.symbol] = true
                genes.push
                    symbol: gene.symbol
                    hgnc_id: gene.hgnc_id
                    name: gene.name

            variant.uniqueGenes = genes

            return attrs


    { Result }
