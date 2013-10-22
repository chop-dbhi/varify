define [
    'environ'
    'mediator'
    'jquery'
    'underscore'
    'backbone'
    'utils/numbers'
    './templates'
    '../utils'
    'app/review/models'
], (environ, mediator, $, _, Backbone, Numbers, Templates, utils, Models) ->


    class Result extends Backbone.View
        initialize: ->
            @model.on 'change', @render

        render: =>
            attrs = @model.attributes
            content = []

            content.push "<h4>#{ attrs.sample.label } <small>in #{ attrs.sample.project }</small></h4>"
            content.push '<ul class=unstyled>'

            content.push "<li><small>Variant Result ID </small>#{ attrs.id }</li>"

            labelClass = utils.depthClass attrs.read_depth

            content.push "
                <li><small>Coverage</small>
                    <span class=#{ labelClass }>#{ attrs.read_depth }x</span> <span class=muted>(<span title=Ref>#{ attrs.read_depth_ref }</span>/<span title=Alt>#{ attrs.read_depth_alt }</span>)</span>
                </li>
            "
            content.push "<li><small>Raw Coverage</small> "
            if attrs.raw_read_depth?
                content.push "#{ attrs.raw_read_depth }x"
            else
                content.push '<span class=muted>n/a</span>'
            content.push '</li>'


            labelClass = utils.qualityClass attrs.quality
            content.push "
                <li><small>Quality</small>
                    <span class=#{ labelClass }>#{ attrs.quality }</span>
                </li>
            "

            content.push "<li style=word-wrap:break-word><small>Genotype</small> #{ attrs.genotype_value } <small>(#{ attrs.genotype_description })</small></li>"

            content.push "<li><small>Base Counts</small> "

            if attrs.base_counts
                bases = []
                for key, value of attrs.base_counts
                    bases.push "#{ key }=#{ value }"
                content.push bases.sort().join(', ')
            else
                content.push '<span class=muted>n/a</span>'
            content.push '</li>'

            content.push '</ul>'

            @$el.html content.join ''

    class ReviewModal extends Backbone.View
        el: '#review-modal'
         
        initialize: ->
            # Execute save handlers in the context of this view 
            _.bindAll(this, 'onSaveSuccess', 'onSaveError')
            
            @assessmentView = new AssessmentView
            @saveButton = $ '#save-assessment-button'
            @auditTrailButton = $ '#audit-trail-button'

        update: (summaryView, resultView) ->
            @selectedSummaryView = summaryView
            @model = summaryView.model
            @options.resultView = resultView

            #Create a new view for the detailed variant information
            @detailedView = new VariantDetails
                model: @model
                resultView: @options.resultView
                metrics: new Models.AssessmentMetrics({}, {variant_id: summaryView.variantId, sample_result: @model.id})

            # Update the modal dialog with the new variant data 
            detailContainer = $ '#review-modal #variant-details-content'
            
            if detailContainer?
                detailContainer.html @detailedView.render
           
            #Create a new view for the knowledge capture form
            assessmentModel = new Models.Assessment({ sample_result: @model.id })

            if @model.get('assessment')?
                assessmentModel.id = @model.get('assessment').id
            
            @assessmentView.update(assessmentModel) 

            @$el.modal('show')

        events: {
            'click #close-review-button': 'close',
            'click #save-assessment-button': 'saveAndClose'
            'click #variant-details-link': 'hideButtons'
            'click #knowledge-capture-link': 'showButtons'
        }

        hideButtons: ->
            @saveButton.hide()
            @auditTrailButton.hide()

        showButtons: ->
            @saveButton.show()
            @auditTrailButton.show()

        close: ->
            @$el.modal('hide')

        saveAndClose: (event) ->
            if @assessmentView.isValid()
                @assessmentView.model.save(null, {success: @onSaveSuccess, error: @onSaveError})
                @$el.modal('hide')

        showNotification: () ->
            $('#review-notification').show()
            setTimeout(@hideNotification, 5000)

        hideNotification: () ->
            $('#review-notification').removeClass('alert-error alert-success')
            $('#review-notification').hide()

        onSaveError: (model, response) ->
            $('#review-notification').html "Error saving knowledge capture data."
            $('#review-notification').addClass('alert-error')
            this.showNotification()

        onSaveSuccess: (model, response) ->
            $('#review-notification').html "Saved changes."
            $('#review-notification').addClass('alert-success')
            this.showNotification()
            @selectedSummaryView.model.fetch()

    class AssessmentView extends Backbone.View
        el: '#knowledge-capture-content'

        initialize: ->
            # Execute render in the context of this view since it is used as
            # the callback for event handlers
            _.bindAll(this, 'onAssessmentFetchSuccess', 'onAssessmentFetchError') 
           
            @formContainer = $('#knowledge-capture-form-container').hide()
            @feedbackContainer = $('#knowledge-capture-feedback-container').show()

            @saveButton = $('#save-assessment-button').hide()
            @auditButton = $('#audit-trail-button').hide()

            @errorContainer = $('#error-container').hide()
            @errorMsg = $('#error-message')

        update: (model) ->
            @model = model
            @model.fetch({
                error: @onAssessmentFetchError
                success: @onAssessmentFetchSuccess
            })

        events: {
            'change input[name=pathogenicity-radio]': 'pathogenicityRadioChanged',
            'click .alert-error > .close': 'closeFormErrorsClicked' 
        }

        onAssessmentFetchError: ->
            @formContainer.hide()
            @feedbackContainer.hide()
            @errorContainer.show()
            @errorMsg.html('<h5 class=text-error>Error retrieving knowledge capture data.</h5>')
            @saveButton.hide()
            @auditButton.hide()

        onAssessmentFetchSuccess: ->
            @errorContainer.hide()
            @feedbackContainer.hide()
            @formContainer.show()
            @render()

        closeFormErrorsClicked: (event) ->
            $(event.target).parent().hide()

        # Enable/disable category radios if the pathogenicity changed
        pathogenicityRadioChanged: (event) ->
            if $(event.target).hasClass('requires-category')
                $('input:radio[name=category-radio]').removeAttr('disabled')
                $('.assessment-category-label').removeClass('muted')
                this.setRadioChecked('category-radio', @model.get('assessment_category'))
            else
                $('input:radio[name=category-radio]:checked').attr('checked', false)
                $('input:radio[name=category-radio]').attr('disabled', true)
                $('.assessment-category-label').addClass('muted')

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

            if (@model.get('pathogenicity') >= 2 && @model.get('pathogenicity') <= 4)
                if !(@model.get('assessment_category')?)
                    valid = false
                    @errorMsg.append('<h5>Please select a category.</h5>')
            if (@model.get('mother_result') == "")
                valid = false
                @errorMsg.append('<h5>Please select a result from the &quot;Mother&quot; dropdown.</h5>')
            if (@model.get('father_result') == "")
                valid = false
                @errorMsg.append('<h5>Please select a result from the &quot;Father&quot; dropdown.</h5>')
            if !(@model.get('sanger_requested')?)
                valid = false
                @errorMsg.append('<h5>Please select true or false for the &quot;Sanger Requested&quot; option.</h5>')

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

    # Represents a summarized view of variant information.
    class VariantSummary extends Backbone.View
        className: 'area-container variant-container'

        tagName: 'tr'

        events:
            'click td': () ->
                mediator.publish 'review/summary/click', this, @options.resultView
            
        initialize: ->
            @model.on 'change', @render
            
            @$el.addClass 'loading'

            @model.on 'change', =>
                @$el.removeClass 'loading'

            @variantId = @options.variantId

        render: =>
            attrs = @model.get('variant')
            assessment = @model.get('assessment')

            $geneNames = $(Templates.geneLinks(attrs.uniqueGenes, true))
                .addClass('genes')

            $genomicPosition = $(Templates.genomicPosition(attrs.chr, attrs.pos))
                .addClass('genomic-position')
            $genomicPosition.append($(Templates.category(assessment)))

            $hgvsP = $(Templates.hgvsP(attrs.effects[0]))
                .addClass('hgvs-p')

            $variantEffects = $(Templates.variantEffects(attrs.effects, true))
                .addClass('variant-effects')
                .append($(Templates.pathogenicity(assessment)))

            # NOTE: As of Bootstrap 2.3.1 there is still an issue with adding
            # tooltips to <td> elements directly as the tooltip will be 
            # instered directly into the table, causing the row to be 
            # misaligned. The workaround(added in 2.3.0) is to
            # set the container to body so that the div is not jammed into the
            # table all willy-nilly like.
            $hgvsC = $(Templates.hgvsC(attrs.effects[0]))
                .addClass('hgvs-c')
                .tooltip({container: 'body'})
            
            $resultGenotype = $(Templates.genotype(@model.get('genotype_value'), @model.get('genotype_description')))
                .addClass('genotype')
                .tooltip({container: 'body'})

            # floating..
            $condensedFlags = $ Templates.condensedFlags(attrs)
            
            @$el.html ''
            @$el.append $geneNames, $hgvsP, $variantEffects, $hgvsC, $resultGenotype, $genomicPosition, $condensedFlags

            return @$el

    class VariantDetails extends Backbone.View
        initialize: ->
            @$content = $('<div class="content">')
            @$el.append @$content
           
            _.bindAll(this, 'fetchMetricsSuccess')
            @metrics = @options.metrics
            @metrics.fetch({success: @fetchMetricsSuccess, error: @fetchMetricsError})

        renderCohorts: (attrs) ->
            return "<h4>Cohorts</h4>#{ Templates.cohortVariantDetailList(attrs.cohorts) }"

        renderPredictions: (attrs) ->
            content = []
            content.push '<h4>Prediction Scores</h4>'
            content.push '<ul class=unstyled>'
                   
            if (sift = attrs.sift[0]) or (pp2 = attrs.polyphen2[0])
                # SIFT
                if sift
                    labelClass = ''
                    switch sift.prediction
                        when 'Damaging' then labelClass = 'text-error'
                        else labelClass = 'muted'
                    content.push "<li><small>SIFT</small> <span class=#{ labelClass }>#{ sift.prediction }</span></li>"

                # PolyPhen2
                if pp2
                    labelClass = ''
                    switch pp2.prediction
                        when 'Probably Damaging' then labelClass = 'text-error'
                        when 'Possibly Damaging' then labelClass = 'text-warning'
                        else labelClass = 'muted'
                    content.push "<li><small>PolyPhen2</small> <span class=#{ labelClass }>#{ pp2.prediction }</span></li>"
                content.push '</ul>'
            else
                content.push '<p class=muted>No predictions scores</p>'

            return content.join ''
        
        renderSummary: (attrs) ->
            content = []
            content.push '<ul class=unstyled>'

            content.push "<li><small>Position</small> #{ Templates.genomicPosition(attrs.chr, attrs.pos) }</li>"

            # List of unique genes (and links)
            content.push "<li><small>Genes</small> #{ Templates.geneLinks(attrs.uniqueGenes) }</li>"

            hgmdLinks = Templates.hgmdLinks(attrs.phenotypes)
            if hgmdLinks
                content.push "<li><small>HGMD IDs</small> #{ hgmdLinks }</li>"

            # dbSNP ID (and link)
            if attrs.rsid
                content.push "<li><small>dbSNP</small> #{ Templates.dbSNPLink(attrs.rsid) }</li>"

            content.push '</ul>'

            content.push "<a href='#{ App.alamut_url }/show?request=chr#{ attrs.chr }:g.#{ attrs.pos }#{ attrs.ref }>#{ attrs.alt }' target=_blank class='btn btn-primary btn-small alamut-button'>Query Alamut</a>"
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

                    # Group by - amino acid change
                    for change, _effs of _.groupBy(effs, (eff) -> eff.hgvs_p or eff.amino_acid_change)
                        content.push '<li>'
                        content.push "<small>#{ change or 'Non-coding' }</small>"
                        content.push '<ul>'

                        for eff in _effs
                            content.push '<li>'
                            if eff.hgvs_c
                                content.push "#{ eff.hgvs_c } "
                            if eff.segment
                                content.push "#{ eff.segment } "
                            if (transcript = eff.transcript)?
                                content.push "<small><a href=\"http://www.ncbi.nlm.nih.gov/nuccore/#{ transcript.transcript }\">#{ transcript.transcript }</a></small> "
                                if attrs.uniqueGenes.length > 1 and (gene = transcript.gene) and gene
                                    content.push "<small>for <a target=_blank href=\"http://www.genenames.org/data/hgnc_data.php?hgnc_id=#{ gene.hgnc_id }\">#{ gene.symbol }</a></small> "
                            content.push '</li>'
                        content.push '</ul></li>'
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

        fetchMetricsError: ->
            $('#assessment-metrics').html('<p class=text-error>Error loading metrics.</p>')

        fetchMetricsSuccess: ->
            $('#assessment-metrics').html('')
            
            hasMetrics = false
            _.each @metrics.get('metrics'), (metrics, name) ->
                if (metrics.count > 0)
                    content = []
                    content.push "<li><small>#{ name }</small>"
                    content.push "#{ Numbers.prettyNumber(metrics.percentage) }%"
                    content.push "(#{ metrics.count })</li>"
                    
                    hasMetrics = true
                    $('#assessment-metrics').append(content.join ' ')

            if not hasMetrics
                $('#assessment-metrics').html('No assessments have been made on this variant')

        renderAssessmentMetricsContainer: ->
            content = []
            content.push '<h4>Assessment Metrics</h4>'

            content.push '<ul class=unstyled id=assessment-metrics><li><img src="/static/images/loader-tiny.gif" /></li></ul>'

            return content.join ''

        _span: (html, size=12) ->
            $("<div class=\"span#{size}\" />").html(html)

        render: =>
            attrs = @model.get('variant')
            
            $row1 = $('<div class=row-fluid />')
            $row2 = $('<div class=row-fluid />')
            $row3 = $('<div class=row-fluid />')

            summarySpan = @_span @options.resultView.$el, 3
            summarySpan.append @renderSummary(attrs)

            $row1.append summarySpan
            $row1.append @_span @renderEffects(attrs), 3
            $row1.append @_span @renderPhenotypes(attrs), 3
            $row1.append @_span @renderPredictions(attrs), 3

            $row2.append @_span @renderCohorts(attrs), 4
            $row2.append @_span @render1000g(attrs), 4
            $row2.append @_span @renderEvs(attrs), 4

            $row3.append @_span @renderPubmed(attrs), 4 
            $row3.append @_span @renderAssessmentMetricsContainer(), 8

            @$content.append $row1, $row2, $row3

            return @$el


    { Result, VariantDetails, VariantSummary, AssessmentView, ReviewModal }
