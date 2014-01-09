define [
    'underscore'
    'marionette'
    '../../utils'
    'cilantro/utils/numbers'
    'tpl!templates/varify/empty.html'
], (_, Marionette, utils, Numbers, templates...) ->

    templates = _.object ['empty'], templates


    class BaseCell extends Marionette.ItemView
        # TODO: Should these different cells have the HTML in a template
        # rather than generating it all here?
        template: templates.empty

        tagName: 'td'


    class CondensedFlags extends BaseCell
        className: 'flags-container'

        onRender: ->
            flags = []

            # dbSNP
            flags.push ['dbSNP', @options.variant['rsid']?]

            # HGMD
            flags.push ['HGMD', _.pluck(@options.variant['phenotypes'], 'hgmd_id').length > 0]

            # 1000g
            flags.push ['1000g', @options.variant['1000g'].length > 0]

            # EVS
            flags.push ['EVS', @options.variant['evs'].length > 0]

            html = []
            for [label, present] in flags
                klass = if present then 'text-info' else 'muted'
                html.push "<span class=\"flag #{ klass }\">#{ label }</span>"

            @$el.html("<span class=flags>#{ html.join('') }<span>")


    class Gene extends BaseCell
        className: 'genes'

        _getGeneHtml: (gene) ->
            name = gene.name or ''

            if gene.hgnc_id
                return "<a title=\"#{ name }\" target=_blank href=\"http://www.genenames.org/data/hgnc_data.php?hgnc_id=#{ gene.hgnc_id }\">#{ gene.symbol }</a>"

            return "<span title=\"#{ name }\">#{ gene.symbol }</span>"

        onRender: ->
            genes = @options.genes

            if not genes? or not genes.length
                @$el.html("<span class=muted>Unknown</span>")
            else if @options.collapse or genes.length is 1
                @$el.html(@_getGeneHtml(genes[0]))
            else
                @$el.html((@_getGeneHtml gene for gene in genes).join(', '))


    class GenomicPosition extends BaseCell
        className: 'genomic-position'

        _getCategoryHtml: (assessment) ->
            if assessment? and assessment.assessment_category?
                html = []
                html.push '<br />Category:'
                html.push assessment.assessment_category.name

                if assessment.assessment_category.id > 2
                    html.push '<span class="muted">(Incidental Finding)</span>'

                return "<span class='assessment-category'>#{ html.join(' ') }</span>"
            else
                return ''

        onRender: ->
            pchr = Numbers.toDelimitedNumber(@options.position)

            position_html = "<a target=_blank href=\"http://genome.ucsc.edu/cgi-bin/hgTracks?position=chr#{ @options.chromosome }%3A#{ @options.position }\">chr#{ @options.chromosome } <span class=muted>@</span> #{ pchr }</a>"

            category_html = @_getCategoryHtml(@options.assessment)

            @$el.html("#{ position_html }#{ category_html }")

    class Genotype extends BaseCell
        className: 'genotype'

        onRender: ->
            if @options.value?
                @$el.attr('title', "#{ @options.value } (#{ @options.description or 'N/A' })")
                @$el.html("#{ @options.value } <small>(#{ @options.description or 'N/A' })</small>")

                # NOTE: As of Bootstrap 2.3.1 there is still an issue with
                # adding tooltips to <td> elements directly as the tooltip will
                # be instered directly into the table, causing the row to be
                # misaligned. The workaround(added in 2.3.0) is to set the
                # container to body so that the div is not jammed into the
                # table all willy-nilly like.
                @$el.tooltip({container: 'body'})
            else
                @$el.html('N/A')


    class HgvsC extends BaseCell
        className: 'hgvs-c'

        onRender: ->
            hgvs_c = "N/A"

            if @options.effects?.length > 0
                effect = @options.effects[0]

                if effect.hgvs_c?
                    @$el.attr('title', effect.hgvs_c or '')

                    # NOTE: As of Bootstrap 2.3.1 there is still an issue with
                    # adding tooltips to <td> elements directly as the tooltip
                    # will be instered directly into the table, causing the
                    # row to be misaligned. The workaround(added in 2.3.0) is
                    # to set the container to body so that the div is not
                    # jammed into the table all willy-nilly like.
                    @$el.tooltip({container: 'body'})

                hgvs_c = "#{ effect.hgvs_c or 'N/A' }"

            @$el.html(hgvs_c)


    class HgvsP extends BaseCell
        className: 'hgvs-p'

        onRender: ->
            hgvs_p = "N/A"

            if @options.effects?.length > 0
                effect = @options.effects[0]
                hgvs_p = "#{ effect.hgvs_p or effect.amino_acid_change or 'N/A' }"

            @$el.html(hgvs_p)


    class VariantEffect extends BaseCell
        className: 'variant-effects'

        _getEffectHtml: (effect) ->
            html = []
            html.push "#{ effect.type }"
            if effect.transcript?
                html.push '<small>'
                html.push effect.transcript.transcript
                if effect.segment?
                    html.push " @ #{ effect.segment }"
                html.push '</small>'
            html.push '</small>'
            return html.join ' '

        _getPathogenicityHtml: (assessment) ->
            if assessment? and assessment.pathogenicity?
                html = []
                html.push '<br />Pathogenicity: '
                html.push assessment.pathogenicity.name
                return "<span class='pathogenicity'>#{ html.join('') }</span>"
            else
                return ''

        onRender: ->
            effects = @options.effects

            if not effects? or not effects.length
                effect_html = '<span class=muted>No Effects</span>'
            else if @options.collapse or effects.length is 1
                labelClass = utils.priorityClass(utils.effectImpactPriority(effects[0].impact))
                effect_html = "<span class='#{ labelClass }'>#{ @_getEffectHtml(effects[0]) }</span>"
            else
                effect_html = (@_getEffectHtml effect for effect in effects).join(', ')

            pathogenicity_html = @_getPathogenicityHtml(@options.assessment)

            @$el.html("#{ effect_html }#{ pathogenicity_html }")

    { CondensedFlags, Gene, GenomicPosition, Genotype, HgvsC, HgvsP, VariantEffect }
