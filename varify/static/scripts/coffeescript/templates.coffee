define [
    'underscore'
    './utils'
    'cilantro/utils/numbers'
], (_, utils, Numbers) ->

    # Renders a genomic position hyperlink based on chr and pos
    genomicPosition = (chr, pos) ->
        pchr = Numbers.toDelimitedNumber(pos)
        return "<td class=genomic-position><a target=_blank href=\"http://genome.ucsc.edu/cgi-bin/hgTracks?position=chr#{ chr }%3A#{ pos }\">chr#{ chr } <span class=muted>@</span> #{ pchr }</a></td>"

    phenotypeScore = (resultScore) ->
        if resultScore?
            rank = parseInt(resultScore.rank)
            score = parseFloat(resultScore.score)

            if not isNaN(rank) and not isNaN(score)
                return "<td>#{ rank } <small class=muted>(#{ score })</small></td>"

        return "<td></td>"

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

        else if collapse or len is 1
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

        else if collapse or len is 1
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
            cohortHtml = "<small>#{ cohort.name }</small> #{ Numbers.prettyNumber(cohort.af * 100) }% <span class=muted>(#{ cohort.size })</span>"

            sampleNames = []
            for sample in _.sortBy(cohort.samples, (s) -> s.name)
                samplePath = "/workspace/samples/#{ sample.id }"
                sampleNames.push "<a href='#{ utils.toAbsolutePath(samplePath) }/'>#{ sample.name }</a>"

            sampleHtml = sampleNames.join('<br />')

            # Hack to encode the sample html so the popover content won't
            # break the html of the page.
            popoverHtml = "<div>#{ $('<div />').html(sampleHtml).html() }</div>"

            html.push "<li class=cohort-details><a href='#' class=cohort-sample-popover title='Samples in Cohort' data-html='true' data-placement=right data-trigger=click data-content='#{ popoverHtml }'>#{ cohortHtml }</a></li>"

        return "<ul class=unstyled>#{ html.join('') }</ul>"

    dbSNPLink = (rsid) ->
        return "<a target=_blank href=\"http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=#{ rsid }\">#{ rsid }</a>"

    assessmentMetrics = (items, usernamePopover=false) ->
        html = []

        _.each items, (item, key) ->
            call_indicator = if item.is_user_call then "*" else ""
            name = if key? and key isnt "" then key else "N/A"

            prefixHtml = "<small>#{ name }</small>  #{ Numbers.prettyNumber(item.percentage) }% "
            countHtml = "<span class=muted>(#{ item.count })#{ call_indicator }</span>"

            if item.usernames.length > 0 and usernamePopover
                usernames = []
                for username in item.usernames
                    usernames.push username
                popoverHtml = usernames.join('<br />')

                countHtml = "<a href='#' class=username-popover data-trigger=hover title='Users who made this call:' data-html=true data-placement=top data-content='#{ popoverHtml }'>#{ countHtml }</a>"

            html.push "<li>#{ prefixHtml }#{ countHtml }</li>"

         return "<ul class=unstyled>#{ html.join('') }</ul>"

     assessmentRows = (assessments) ->
        html = []

        # Group the assessments by pathogenicity where the result is an object
        # with properties as pathogenicities and the values being arrays of
        # assessments with that pathogenicity.
        groupedAssessments = _.chain(assessments).groupBy('pathogenicity').value()
        _.each groupedAssessments, (assessmentList, pathogenicity) ->
            for assessment in assessmentList
                assessmentHasDetails = assessment.details?

                html.push "<tr id=assessment-row-#{ assessment.id }>"

                if assessmentHasDetails
                    html.push "<td><a href=#><i class=icon-plus></i><i class='icon-minus hide'></i></a></td>"
                else
                    html.push "<td></td>"

                samplePath = "/workspace/samples/#{ assessment.sample.id }"
                html.push "<td><a href='#{ utils.toAbsolutePath(samplePath) }/'>#{ assessment.sample.name }</a></td>"

                if not _.isEmpty(assessment.user.email)
                    html.push "<td><a href='mailto:#{ assessment.user.email }'>#{ assessment.user.username }</a></td>"
                else
                    html.push  "<td>#{ assessment.user.username }</td>"

                html.push "<td>#{ assessment.pathogenicity }</td>"
                html.push "<td>#{ assessment.category }</td>"
                html.push "<td>#{ assessment.mother_result }</td>"
                html.push "<td>#{ assessment.father_result }</td>"
                html.push "<td>#{ assessment.sanger }</td>"

                html.push '</tr>'

                if assessmentHasDetails
                    html.push "<tr class='hide no-border' id=assessment-row-#{ assessment.id}-details><td></td><td colspan='7'><strong>Evidence Details: </strong>#{ assessment.details }</td></tr>"

        return html.join('')

    hgmdLinks = (phenotypes) ->
        return (p.hgmd_id for p in phenotypes when p.hgmd_id?).join(', ')

    {
        assessmentMetrics,
        assessmentRows,
        category,
        cohortVariantDetailList,
        condensedFlags,
        dbSNPLink,
        hgmdLinks,
        hgvsC,
        hgvsP,
        geneLinks,
        genomicPosition,
        genotype,
        pathogenicity,
        phenotypeScore,
        variantEffects,
    }

