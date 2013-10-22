define [
    'environ'
    'underscore'
    'utils/numbers'
    '../utils'
], (environ, _, Numbers, utils) ->

    # Renders a genomic position hyperlink based on chr and pos
    genomicPosition = (chr, pos) ->
        pchr = Numbers.toDelimitedNumber(pos)
        return "<td class=genomic-position><a target=_blank href=\"http://genome.ucsc.edu/cgi-bin/hgTracks?position=chr#{ chr }%3A#{ pos }\">chr#{ chr } <span class=muted>@</span> #{ pchr }</a></td>"


    _renderGene = (gene) ->
        name = gene.name or ''
        if gene.hgnc_id
            return "<a title=\"#{ name }\" target=_blank href=\"http://www.genenames.org/data/hgnc_data.php?hgnc_id=#{ gene.hgnc_id }\">#{ gene.symbol }</a>"
        return "<span title=\"#{ name }\">#{ gene.symbol }</span>"

    category = (assessment) ->
        if assessment? and assessment.assessment_category?
            html = []
            html.push '<br />Category:'
            html.push assessment.assessment_category.name

            if assessment.assessment_category.id > 2
                html.push '<span class="muted">(Incidental Finding)</span>'

            return "<span class='assessment-category'>#{ html.join(' ') }</span>"
        else
            return ''

    pathogenicity = (assessment) ->
        if assessment? and assessment.pathogenicity?
            html = []
            html.push '<br />Pathogenicity: '
            html.push assessment.pathogenicity.name
            return "<span class='pathogenicity'>#{ html.join('') }</span>"
        else
            return ''

    # Render a list of gene names hyperlinks
    # Takes an array of gene objects with `symbol`, `hgnc_id` and `name`
    geneLinks = (genes, collapse=false) ->
        html = []
        len = genes.length

        if not len
            html.push '<span class=muted>Unknown</span>'

        else if collapse or len isnt 1
            html.push _renderGene genes[0]
        else
            html.push (_renderGene gene for gene in genes).join(', ')
        
        return "<td>#{ html.join(' ') }</td>"

    hgvsC = (eff) ->
        if eff?
            text = eff.hgvs_c or ''
            "<td title='#{ text }'>#{ text }</td>"
        else
            "<td></td>"

    genotype = (value, description) ->
        title = "#{ value } (#{ description })"
        return "<td title='#{ title }'>#{ value } <small>(#{ description })</small></td>"

    hgvsP = (eff) ->
        if eff?
            "<td>#{ eff.hgvs_p or eff.amino_acid_change or '' }</td>"
        else
            "<td></td>"

    _renderVariantEffect = (eff) ->
        html = []
        html.push "#{ eff.type }"
        if eff.transcript?
            html.push '<small>'
            html.push eff.transcript.transcript
            if eff.segment?
                html.push " @ #{ eff.segment }"
            html.push '</small>'
        html.push '</small>'
        html.join ' '


    variantEffects = (effects, collapse=false) ->
        html = []
        len = effects.length

        if not len
            return '<span class=muted>No Effects</span>'

        else if collapse or len isnt 1
            labelClass = utils.priorityClass(utils.effectImpactPriority(effects[0].impact))
            html.push "<span class=\"#{ labelClass }\">#{ _renderVariantEffect effects[0] }</span>"
        else
            html.push (_renderVariantEffect eff for eff in effects).join(', ')

        return "<td>#{ html.join(' ') }</td>"

    _renderTranscript = (effect) ->
        if not (effect.transcript)? then return ''
        content.push "<a href=\"http://www.ncbi.nlm.nih.gov/nuccore/#{ transcript.transcript }\">#{ transcript.transcript }</a></small> "
        if attrs.uniqueGenes.length > 1 and (gene = transcript.gene) and gene
            content.push "<small>for <a target=_blank href=\"http://www.genenames.org/data/hgnc_data.php?hgnc_id=#{ gene.hgnc_id }\">#{ gene.symbol }</a></small> "


    # Contains flags for dbSNP, HGMD, 1000G, EVS
    condensedFlags = (attrs) ->
        flags = []

        # dbSNP
        flags.push ['dbSNP', attrs['rsid']?]

        # HGMD
        flags.push ['HGMD', _.pluck(attrs['phenotypes'], 'hgmd_id').length > 0]

        # 1000g
        flags.push ['1000g', attrs['1000g'].length > 0]

        # EVS
        flags.push ['EVS', attrs['evs'].length > 0]

        html = []
        for [label, present] in flags
            klass = if present then 'text-info' else 'muted'
            html.push "<span class=\"flag #{ klass }\">#{ label }</span>"
        return "<td class=flags-container><span class=flags>#{ html.join('') }<span></td>"

    cohortVariantDetailList = (cohorts) ->
        html = []
        for cohort in cohorts
            html.push "<li><small>#{ cohort.name }</small> #{ Numbers.prettyNumber(cohort.af * 100) }% <span class=muted>(#{ cohort.size })</span></li>"
        return "<ul class=unstyled>#{ html.join('') }</ul>"

    dbSNPLink = (rsid) ->
        return "<a target=_blank href=\"http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=#{ rsid }\">#{ rsid }</a>"


    hgmdLinks = (phenotypes) ->
        return (p.hgmd_id for p in phenotypes when p.hgmd_id?).join(', ')

    {
        category,
        pathogenicity,
        genomicPosition,
        geneLinks,
        hgvsP,
        hgvsC,
        genotype,
        variantEffects,
        condensedFlags,
        dbSNPLink,
        cohortVariantDetailList,
        hgmdLinks,
    }
