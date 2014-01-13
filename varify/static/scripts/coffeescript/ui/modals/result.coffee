define [
    'underscore'
    'marionette'
    '../../models'
    '../../utils'
    'tpl!templates/varify/empty.html'
    'tpl!templates/varify/modals/result.html'
    'tpl!templates/varify/modals/result/details.html'
    'tpl!templates/varify/modals/result/assessment.html'
], (_, Marionette, models, utils, templates...) ->

    templates = _.object ['empty', 'result', 'details', 'assessment'], templates


    class DetailsTab extends Marionette.ItemView
        template: templates.details

        className: 'tab-pane active'

        ui:
            assessmentMetrics: '#assessment-metrics'
            row1: '.details-row-1'
            row2: '.details-row-2'
            row3: '.details-row-3'

        initialize: ->
            @metrics = @options.metrics

            @$el.attr('id', 'variant-details-content')

        metricsFetchSuccess: =>
            if _.isEmpty(@metrics.get('metrics'))
                @ui.assessmentMetrics.html('No assessments have been made on this variant')
            else
                metrics = @metrics.get('metrics')
                content = []

                # Pathogenicity and Category Row
                content.push '<div class=row-fluid>'

                content.push '<div class=span4>'
                # content.push "<strong>Pathogenicities</strong>#{ Templates.assessmentMetrics(metrics.pathogenicities, true) }"
                content.push '</div>'

                content.push '<div class=span4>'
                # content.push "<strong>Categories</strong>#{ Templates.assessmentMetrics(metrics.categories, true) }"
                content.push '</div>'

                content.push '</div>'

                # Individual assessment breakdown table row
                content.push '<div class=row-fluid>'

                content.push '<table class=assessment-details-table>'
                content.push '<thead><tr><th></th><th>Sample</th><th>User</th><th>Pathogenicity</th><th>Category</th><th>Mother</th><th>Father</th><th>Sanger Requested</th></tr></thead>'

                # content.push "<tbody>#{ Templates.assessmentRows(metrics.assessments) }</tbody>"

                content.push '</table>'
                content.push '</div>'

                $(@ui.assessmentMetrics)
                    .empty()
                    .append(content.join ' ')

                $('.username-popover').popover()

        metricsFetchError: =>
            @ui.assessmentMetrics.html('<p class=text-error>Error loading metrics.</p>')

        renderAssessmentMetricsContainer: ->
            content = []
            content.push '<h4>Assessments</h4>'

            content.push "<div id=assessment-metrics><img src='#{ utils.getRootUrl('/static/images/loader-tiny.gif') }' /></div>"

            return content.join ''

        ###
        render: =>
            @$el.append @renderAssessmentMetricsContainer()

            @metrics.fetch
                success: @metricsFetchSuccess
                error: @metricsFetchError

            return @$el
        ###

    class AssessmentTab extends Marionette.ItemView
        template: templates.assessment

        className: 'tab-pane'

        initialize: ->
            @$el.attr('id', 'knowledge-capture-content')


    class ResultDetails extends Marionette.ItemView
        className: 'modal hide'

        template: templates.result

        ui:
            tabContent: '.tab-content'

        onRender: ->
            @$el.modal
                show: false
                keyboard: false
                backdrop: 'static'

        update: (result) ->
            @ui.tabContent.empty()

            @model = result

            metrics = new models.AssessmentMetrics(
                {},
                {variant_id: result.get('variant').id, result_id: result.id})

            @detailsTab = new DetailsTab
                model: result
                metrics: metrics
            @ui.tabContent.append @detailsTab.render().el

            @assessmentTab = new AssessmentTab
                result_id: result.id
            @ui.tabContent.append @assessmentTab.render().el

            @$el.modal('show')

    { ResultDetails }
