define [
    'underscore'
    'marionette'
    '../../models'
    '../../utils'
    '../../templates'
    'cilantro/utils/numbers'
], (_, Marionette, models, utils, Templates, Numbers) ->

    class DetailsTab extends Marionette.ItemView
        template: 'varify/empty'

        initialize: ->
            @metrics = @options.metrics

            @$content = $('<div class="content">')
            @$el.append @$content
            @$el.attr('id', 'variant-details-content')

        events:
            'click .cohort-sample-popover': (e) ->
                $('.cohort-sample-popover').not(e.target).popover('hide')
            'click .assessment-details-table .icon-plus': 'expandAssessmentRow'
            'click .assessment-details-table .icon-minus': 'collapseAssessmentRow'

        expandAssessmentRow: (event) =>
            # Figure out which row we clicked on
            row = $(event.target).closest('tr')

            # Lookup the details row
            detailsRow = $("##{ row.attr('id') }-details")

            # Hide the expand(+) control, show the collapse(-) control, and
            # show the details row.
            detailsRow.show()
            $(event.target).addClass('hide')
            row.find('.icon-minus').removeClass('hide')

        collapseAssessmentRow: (event) =>
             # Figure out which row we clicked on
            row = $(event.target).closest('tr')

            # Lookup the details row
            detailsRow = $("##{ row.attr('id') }-details")

            # Show the expand(+) control, hide the collapse(-) control, and
            # hide the details row.
            detailsRow.hide()
            $(event.target).addClass('hide')
            row.find('.icon-plus').removeClass('hide')

        renderCohorts: (attrs) ->
            content = []
            content.push "<h4>Cohorts</h4>"

            if attrs.cohorts? and attrs.cohorts.length
                content.push "#{ Templates.cohortVariantDetailList(attrs.cohorts) }"
            else
                content.push '<p class=muted>No cohorts</p>'

            return content.join ''

        renderPredictions: (attrs) ->
            content = []
            content.push '<h4>Prediction Scores</h4>'
            content.push '<ul class=unstyled>'

            # SIFT
            if (sift = attrs.sift[0])
                labelClass = ''
                switch sift.prediction
                    when 'Damaging' then labelClass = 'text-error'
                    else labelClass = 'muted'
                content.push "<li><small>SIFT</small> <span class=#{ labelClass }>#{ sift.prediction }</span></li>"

            # PolyPhen2
            if (pp2 = attrs.polyphen2[0])
                labelClass = ''
                switch pp2.prediction
                    when 'Probably Damaging' then labelClass = 'text-error'
                    when 'Possibly Damaging' then labelClass = 'text-warning'
                    else labelClass = 'muted'
                content.push "<li><small>PolyPhen2</small> <span class=#{ labelClass }>#{ pp2.prediction }</span></li>"

            content.push '</ul>'
            if not (sift or pp2)
                content.push '<p class=muted>No predictions scores</p>'

            return content.join ''

        renderSummary: (result_attrs, variant_attrs) ->
            content = []

            content.push "<h4>#{ result_attrs.sample.label } <small>in #{ result_attrs.sample.project }</small></h4>"
            content.push '<ul class=unstyled>'

            content.push "<li><small>Variant Result ID </small>#{ result_attrs.id }</li>"

            labelClass = utils.depthClass result_attrs.read_depth

            content.push "
                <li><small>Coverage</small>
                    <span class=#{ labelClass }>#{ result_attrs.read_depth }x</span> <span class=muted>(<span title=Ref>#{ result_attrs.read_depth_ref }</span>/<span title=Alt>#{ result_attrs.read_depth_alt }</span>)</span>
                </li>
            "
            content.push "<li><small>Raw Coverage</small> "
            if result_attrs.raw_read_depth?
                content.push "#{ result_attrs.raw_read_depth }x"
            else
                content.push '<span class=muted>n/a</span>'
            content.push '</li>'


            labelClass = utils.qualityClass result_attrs.quality
            content.push "
                <li><small>Quality</small>
                    <span class=#{ labelClass }>#{ result_attrs.quality }</span>
                </li>
            "

            content.push "<li style=word-wrap:break-word><small>Genotype</small> #{ result_attrs.genotype_value } <small>(#{ result_attrs.genotype_description })</small></li>"

            content.push "<li><small>Base Counts</small> "

            if result_attrs.base_counts
                bases = []
                for key, value of result_attrs.base_counts
                    bases.push "#{ key }=#{ value }"
                content.push bases.sort().join(', ')
            else
                content.push '<span class=muted>n/a</span>'
            content.push '</li>'

            content.push "<li><small>Position</small> #{ Templates.genomicPosition(variant_attrs.chr, variant_attrs.pos) }</li>"

            # List of unique genes (and links)
            content.push "<li><small>Genes</small> #{ Templates.geneLinks(variant_attrs.uniqueGenes) }</li>"

            hgmdLinks = Templates.hgmdLinks(variant_attrs.phenotypes)
            if hgmdLinks
                content.push "<li><small>HGMD IDs</small> #{ hgmdLinks }</li>"

            # dbSNP ID (and link)
            if variant_attrs.rsid
                content.push "<li><small>dbSNP</small> #{ Templates.dbSNPLink(variant_attrs.rsid) }</li>"

            content.push '</ul>'

            content.push "<a href='http://localhost:10000/show?request=chr#{ variant_attrs.chr }:g.#{ variant_attrs.pos }#{ variant_attrs.ref }>#{ variant_attrs.alt }' target=_blank class='btn btn-primary btn-small alamut-button'>Query Alamut</a>"
            return content.join ''

        render1000g: (attrs) ->
            content = []
            content.push '<h4>1000 Genomes</h4>'

            # 1000G allele frequencies
            if (tg = attrs['1000g'][0])
                content.push '<ul class=unstyled>'
                if tg.all_af?
                    content.push "<li><small>All</small> #{ Numbers.prettyNumber(tg.all_af * 100) }%</li>"
                if tg.amr_af?
                    content.push "<li><small>American</small> #{ Numbers.prettyNumber(tg.amr_af * 100) }%</li>"
                if tg.afr_af?
                    content.push "<li><small>African</small> #{ Numbers.prettyNumber(tg.afr_af * 100) }%</li>"
                if tg.eur_af?
                    content.push "<li><small>European</small> #{ Numbers.prettyNumber(tg.eur_af * 100) }%</li>"
                content.push '</ul>'
            else
                content.push '<p class=muted>No 1000G frequencies</p>'

            return content.join ''

        renderEvs: (attrs) ->
            content = []
            content.push '<h4 title="Exome Variant Server">EVS</h4>'

            # EVS allele frequencies
            if (evs = attrs.evs[0])
                content.push '<ul class=unstyled>'
                if evs.all_af?
                    content.push "<li><small>All</small> #{ Numbers.prettyNumber(evs.all_af * 100) }%</li>"
                if evs.afr_af?
                    content.push "<li><small>African</small> #{ Numbers.prettyNumber(evs.afr_af * 100) }%</li>"
                if evs.eur_af?
                    content.push "<li><small>European</small> #{ Numbers.prettyNumber(evs.eur_af * 100) }%</li>"
                content.push '</ul>'
            else
                content.push '<p class=muted>No EVS frequencies</p>'

            return content.join ''

        renderEffects: (attrs) ->
            content = []
            content.push '<h4>Effects</h4>'

            valid = false
            _.each attrs.effects, (eff) ->
                if eff.transcript? then valid = true

            # Variant effects
            if valid
                content.push '<ul class=unstyled>'

                # Group by - type of effect
                for type, effs of _.groupBy(attrs.effects, 'type')
                    content.push '<li>'

                    labelClass = utils.priorityClass(utils.effectImpactPriority(effs[0].impact))
                    content.push "<span class=#{ labelClass }>#{ type }</span>"

                    content.push '<ul>'

                    for eff in effs
                        content.push '<li>'
                        content.push "<small><a href=\"http://www.ncbi.nlm.nih.gov/nuccore/#{ eff.transcript.transcript }\">#{ eff.transcript.transcript }</a></small> "
                        if attrs.uniqueGenes.length > 1 and (gene = eff.transcript.gene)
                            content.push "<small>for <a target=_blank href=\"http://www.genenames.org/data/hgnc_data.php?hgnc_id=#{ gene.hgnc_id }\">#{ gene.symbol }</a></small> "

                        content.push '<ul><li>'
                        if eff.hgvs_c
                            content.push "#{ eff.hgvs_c } "
                        if eff.segment
                            content.push "#{ eff.segment } "
                        content.push '</li>'

                        if eff.hgvs_p or eff.amino_acid_change
                            content.push "<li>#{ eff.hgvs_p or eff.amino_acid_change }</li>"

                        content.push '</ul>'
                    content.push '</li></ul>'
                content.push '</ul>'
            else
                content.push '<p class=muted>No SNPEff effects known</p>'

            return content.join ''

        renderPhenotypes: (attrs) ->
            content = []
            content.push '<h4>Phenotypes</h4>'

            if attrs.phenotypes[0]
                content.push '<ul class=unstyled>'
                for phenotype in attrs.phenotypes
                    content.push "<li>#{ phenotype.term }"
                    if phenotype.hpo_id or phenotype.hgmd_id
                        content.push '<ul>'
                        if phenotype.hgmd_id
                            content.push "<li><small>HGMD</small> #{ phenotype.hgmd_id }</li>"
                        if phenotype.hpo_id
                            content.push "<li><small>HPO</small> #{ phenotype.hpo_id }</li>"
                        content.push '</ul>'
                    content.push '</li>'
                content.push '</ul>'
            else
                content.push '<p class=muted>No associated phenotypes</p>'

            return content.join ''

        renderPubmed: (attrs) ->
            content = []
            content.push '<h4>Articles</h4>'

            if attrs.articles[0]
                content.push '<ul class=unstyled>'
                for pmid in attrs.articles
                    content.push "<li><a href=\"http://www.ncbi.nlm.nih.gov/pubmed/#{ pmid }\">#{ pmid }</a></li>"
                content.push '</ul>'
            else
                content.push '<p class=muted>No PubMed articles associated</p>'

            return content.join ''

        fetchMetricsError: =>
            $('#assessment-metrics').html('<p class=text-error>Error loading metrics.</p>')

        fetchMetricsSuccess: =>
            $('#assessment-metrics').html('')

            if _.isEmpty(@metrics.get('metrics'))
                $('#assessment-metrics').html('<p class=muted>No assessments have been made on this variant</p>')

            else
                metrics = @metrics.get('metrics')
                content = []

                # Pathogenicity and Category Row
                content.push '<div class=row-fluid>'

                content.push '<div class=span4>'
                content.push "<strong>Pathogenicities</strong>#{ Templates.assessmentMetrics(metrics.pathogenicities, true) }"
                content.push '</div>'

                content.push '<div class=span4>'
                content.push "<strong>Categories</strong>#{ Templates.assessmentMetrics(metrics.categories, true) }"
                content.push '</div>'

                content.push '</div>'

                # Individual assessment breakdown table row
                content.push '<div class=row-fluid>'

                content.push '<table class=assessment-details-table>'
                content.push '<thead><tr><th></th><th>Sample</th><th>User</th><th>Pathogenicity</th><th>Category</th><th>Mother</th><th>Father</th><th>Sanger Requested</th></tr></thead>'

                content.push "<tbody>#{ Templates.assessmentRows(metrics.assessments) }</tbody>"

                content.push '</table>'
                content.push '</div>'

                $('#assessment-metrics').append(content.join ' ')

                $('.username-popover').popover()

        renderAssessmentMetricsContainer: ->
            content = []
            content.push '<h4>Assessments</h4>'

            content.push "<div id=assessment-metrics><img src='#{ utils.toAbsolutePath('static/images/loader-tiny.gif') }' /></div>"

            return content.join ''

        _span: (html, size=12) ->
            $("<div class=\"span#{size}\" />").html(html)

        render: =>
            attrs = @model.get('variant')

            $row1 = $('<div class=row-fluid />')
            $row2 = $('<div class=row-fluid />')
            $row3 = $('<div class="row-fluid  assessments-table-container" />')

            $row1.append @_span @renderSummary(@model.attributes, attrs), 3
            $row1.append @_span @renderEffects(attrs), 3
            $row1.append @_span @renderPhenotypes(attrs), 3
            $row1.append @_span @renderPredictions(attrs), 3

            $row2.append @_span @renderCohorts(attrs), 3
            $row2.append @_span @render1000g(attrs), 3
            $row2.append @_span @renderEvs(attrs), 3
            $row2.append @_span @renderPubmed(attrs), 3

            $row3.append @_span @renderAssessmentMetricsContainer(), 12

            @$content.append $row1, $row2, $row3

            @$el.find('.cohort-sample-popover').popover()

            @metrics.fetch({success: @fetchMetricsSuccess, error: @fetchMetricsError})

            return @$el


    class AssessmentTab extends Marionette.ItemView
        template: 'varify/empty'

        el: '#knowledge-capture-content'

        update: (model) ->
            # If this is the first update call then we need to intialize the UI
            # elements so we can reference them in the success/error handlers
            # in the fetch call we are about to make.
            if not @model?
                @formContainer = $('#knowledge-capture-form-container')
                @feedbackContainer = $('#knowledge-capture-feedback-container')
                @saveButton = $('#save-assessment-button')
                @auditButton = $('#audit-trail-button')
                @errorContainer = $('#error-container')
                @errorMsg = $('#error-message')

                $('.alert-error > .close').on 'click', @closeFormErrorsClicked

            @formContainer.hide()
            @feedbackContainer.show()
            @errorContainer.hide()

            @model = model
            @model.fetch({
                error: @onAssessmentFetchError
                success: @onAssessmentFetchSuccess
            })

        onAssessmentFetchError: =>
            @formContainer.hide()
            @feedbackContainer.hide()
            @errorContainer.show()
            @errorMsg.html('<h5 class=text-error>Error retrieving knowledge capture data.</h5>')
            @saveButton.hide()
            @auditButton.hide()

        onAssessmentFetchSuccess: =>
            @errorContainer.hide()
            @feedbackContainer.hide()
            @formContainer.show()
            @render()

        closeFormErrorsClicked: (event) ->
            $(event.target).parent().hide()

        isValid: ->
            # Rather than checking which field changed, just update all fields
            @model.set({
                evidence_details: $('#evidence-details').val(),
                sanger_requested: $('input[name=sanger-radio]:checked').val(),
                pathogenicity: $('input[name=pathogenicity-radio]:checked').val(),
                assessment_category: $('input[name=category-radio]:checked').val(),
                mother_result: $('#mother-results').val(),
                father_result: $('#father-results').val()
            })

            valid = true

            @errorContainer.hide()
            @errorMsg.html('')

            if _.isEmpty(@model.get('pathogenicity'))
                @errorMsg.append('<h5>Please select a pathogenicity.</h5>')
            if _.isEmpty(@model.get('assessment_category'))
                @errorMsg.append('<h5>Please select a category.</h5>')
            if _.isEmpty(@model.get('mother_result'))
                valid = false
                @errorMsg.append('<h5>Please select a result from the &quot;Mother&quot; dropdown.</h5>')
            if _.isEmpty(@model.get('father_result'))
                valid = false
                @errorMsg.append('<h5>Please select a result from the &quot;Father&quot; dropdown.</h5>')
            if not @model.get('sanger_requested')?
                valid = false
                @errorMsg.append('<h5>Please select one of the &quot;Sanger Requested&quot; options.</h5>')

            if !valid
                @errorContainer.show()

            valid

        # Checks the radio button with the supplied name and value(all other
        # radios with that name are unchecked).
        setRadioChecked: (name, value) ->
            # Lookup all the radio buttons using the supplied name
            radios = $('input:radio[name=' + name + ']')
            # Uncheck any current selection
            $ radios.prop('checked', false)
            # Check the correct radio button based on the supplied value
            checkedRadio = $(radios.filter('[value=' + value + ']'))
            $(checkedRadio.prop('checked', true))
            $(checkedRadio.change())

        render: ->
            this.setRadioChecked('category-radio', @model.get('assessment_category'))
            this.setRadioChecked('pathogenicity-radio', @model.get('pathogenicity'))
            this.setRadioChecked('sanger-radio', @model.get('sanger_requested'))

            $('#mother-results').val(@model.get('mother_result'))
            $('#father-results').val(@model.get('father_result'))
            $('#evidence-details').val(@model.get('evidence_details'))


    class ResultDetails extends Marionette.ItemView
        className: 'modal hide'

        template: 'varify/modals/result'

        ui:
            variantDetailsTabContent: '#variant-details-content'
            saveButton: '#save-assessment-button'
            auditTrailButton: '#audit-trail-button'

        events:
            'click #close-review-button': 'close'
            'click #save-assessment-button': 'saveAndClose'
            'click #variant-details-link': 'hideButtons'
            'click #knowledge-capture-link': 'showButtons'

        initialize: ->
            @assessmentTab = new AssessmentTab

        hideButtons: ->
            @ui.saveButton.hide()
            @ui.auditTrailButton.hide()

        showButtons: ->
            @ui.saveButton.show()
            @ui.auditTrailButton.show()

        saveAndClose: (event) ->
            if @assessmentTab.isValid()
                @assessmentTab.model.save(null, {success: @onSaveSuccess, error: @onSaveError})
                @close()

        close: ->
            @$el.modal('hide')

        onSaveError: (model, response) =>
            $('#review-notification').html "Error saving knowledge capture data."
            $('#review-notification').addClass('alert-error')
            @showNotification()

        onSaveSuccess: (model, response) =>
            $('#review-notification').html "Saved changes."
            $('#review-notification').addClass('alert-success')
            @showNotification()
            @selectedSummaryView.model.fetch()

        showNotification: () ->
            $('#review-notification').show()
            setTimeout(@hideNotification, 5000)

        hideNotification: () ->
            $('#review-notification').removeClass('alert-error alert-success')
            $('#review-notification').hide()

        onRender: ->
            @$el.modal
                show: false
                keyboard: false
                backdrop: 'static'

        update: (summaryView, result) ->
            @selectedSummaryView = summaryView
            @model = result

            metrics = new models.AssessmentMetrics(
                {},
                {variant_id: result.get('variant').id, result_id: result.id})

            @detailsTab = new DetailsTab
                model: result
                metrics: metrics
            @ui.variantDetailsTabContent.html @detailsTab.render

            #Create a new view for the knowledge capture form
            assessmentModel = new models.Assessment
                sample_result: @model.id

            if @model.get('assessment')?
                assessmentModel.id = @model.get('assessment').id

            @assessmentTab.update(assessmentModel)

            @$el.modal('show')

    { ResultDetails }
