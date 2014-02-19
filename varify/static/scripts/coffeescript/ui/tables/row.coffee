define [
    'underscore'
    'marionette'
    'cilantro'
    '../../models'
    '../../templates'
], (_, Marionette, c, models, Templates) ->

    class ResultRow extends Marionette.ItemView
        className: 'area-container variant-container'

        template: 'varify/empty'

        tagName: 'tr'

        events:
            'click': 'onClick'

        onClick: (events) =>
            c.trigger('resultRow:click', this, @model)

        initialize: ->
            @data = {}
            if not (@data.resultPk = @options.resultPk)
                throw new Error 'result pk required'

            @model = new models.Result
                id: @data.resultPk
            @model.on 'sync', @onSync

        onSync: =>
            variant = @model.get('variant')
            resultScore = @model.get('score')
            assessment = @model.get('assessment')

            $gene = $(Templates.geneLinks(variant.uniqueGenes, collapse: true))
                .addClass('genes')

            $hgvsP = $(Templates.hgvsP(variant.effects[0]))
                .addClass('hgvs-p')

            $variantEffects = $(Templates.variantEffects(variant.effects, true))
                .addClass('variant-effects')
                .append($(Templates.pathogenicity(assessment)))

            # NOTE: As of Bootstrap 2.3.1 there is still an issue with adding
            # tooltips to <td> elements directly as the tooltip will be
            # instered directly into the table, causing the row to be
            # misaligned. The workaround(added in 2.3.0) is to
            # set the container to body so that the div is not jammed into the
            # table all willy-nilly like.
            $hgvsC = $(Templates.hgvsC(variant.effects[0]))
                .addClass('hgvs-c')
                .tooltip({container: 'body'})

            $genotype = $(Templates.genotype(@model.get('genotype_value'), @model.get('genotype_description')))
                .addClass('genotype')
                .tooltip({container: 'body'})

            $genomicPosition = $(Templates.genomicPosition(variant.chr, variant.pos))
                .addClass('genomic-position')
                .append($(Templates.category(assessment)))

            $phenotypeScore = $(Templates.phenotypeScore(resultScore))
                .addClass('phenotype-score')

            $condensedFlags = $(Templates.condensedFlags(variant))

            @$el.empty()
            @$el.append $gene, $hgvsP, $variantEffects, $hgvsC, $genotype, $genomicPosition, $phenotypeScore, $condensedFlags

        onRender: =>
            @model.fetch()


    class EmptyResultRow extends c.ui.LoadView
        align: 'left'

        tagName: 'tr'


    { ResultRow, EmptyResultRow }
