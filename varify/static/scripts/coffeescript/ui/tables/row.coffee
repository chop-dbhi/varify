define [
    'underscore'
    'marionette'
    'cilantro/ui/base'
    '../../models'
    './cell'
    'tpl!templates/varify/empty.html'
], (_, Marionette, base, models, cell, templates...) ->

    templates = _.object ['empty'], templates

    class ResultRow extends Marionette.ItemView
        className: 'area-container variant-container'

        template: templates.empty

        tagName: 'tr'

        initialize: ->
            @data = {}
            if not (@data.resultPk = @options.resultPk)
                throw new Error 'result pk required'
            if not (@data.rootUrl = @options.rootUrl)
                throw new Error 'root url required'

            @model = new models.Result
                id: @data.resultPk
                rootUrl: @options.rootUrl
            @model.on 'sync', @onSync

        onSync: =>
            variant = @model.get('variant')
            assessment = @model.get('assessment')

            gene = new cell.Gene
                genes: variant.uniqueGenes
                collapse: true

            hgvsP = new cell.HgvsP
                effects: variant.effects

            variantEffects = new cell.VariantEffect
                effects: variant.effects
                assessment: assessment
                collapse: true

            hgvsC = new cell.HgvsC
                effects: variant.effects

            genotype = new cell.Genotype
                description: @model.get('genotype_description')
                value: @model.get('genotype_value')

            genomicPosition = new cell.GenomicPosition
                chromosome: variant.chr
                position: variant.chr
                assessment: assessment

            condensedFlags = new cell.CondensedFlags
                variant: variant

            @$el.empty()
            @$el.append gene.render().el,
                        hgvsP.render().el,
                        variantEffects.render().el,
                        hgvsC.render().el,
                        genotype.render().el,
                        genomicPosition.render().el,
                        condensedFlags.render().el

        onRender: =>
            @model.fetch()


    class EmptyResultRow extends base.LoadView
        align: 'left'

        tagName: 'tr'


    { ResultRow, EmptyResultRow }
