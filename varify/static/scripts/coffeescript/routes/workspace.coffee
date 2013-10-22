define [
    'environ'
    'mediator'
    'jquery'
    'backbone'
    'serrano'
    'views/counter'
], (environ, mediator, $, Backbone, Serrano, DataContextCounter) ->

    class WorkspaceArea extends Backbone.View
        el: '#workspace-area'

        initialize: ->
            super

            $analysisModalButton = $ '<button class="btn btn-primary" data-toggle=modal data-target="#analysis-modal"><i class=icon-filter></i> Edit Analysis</button>'

            $clearAnalysis = $('[data-toggle=clear-analysis]').click ->
                mediator.publish Serrano.DATACONTEXT_CLEAR

            @datacontextSampleLabel = $('<h4 id=datacontext-sample-label></h4>')
                .appendTo('#subnav .container-fluid')

            # Add an info icon until we figure out a better way to tell the
            # user the sample label is clickable.
            $('<i class="icon-info-sign"></i>')
                .appendTo('#subnav .container-fluid')

            # When the sample changes, update the label
            mediator.subscribe 'analysis/sample/change', (id, name) =>
                @onSampleChanged(id, name)

            # Add button to subnav for editing the current analysis
            $analysisModalButton
                .addClass('pull-right')
                .appendTo('#subnav .container-fluid')

            # While the analysis dialog is open, subscribers can subscribe to
            # these channels to pause their normal handlers from executing
            # as the DataContext changes
            $analysisModal = $('#analysis-modal').on
                show: -> mediator.publish 'analysis/editing/start'
                hide: -> mediator.publish 'analysis/editing/done'

            # Apply the data context counter to the analysis-count on
            # the modal itself
            counter = new DataContextCounter
                el: $analysisModal.find('.modal-footer .analysis-count')

        onSampleChanged: (id, name) ->
            @datacontextSampleLabel.html name

        load: ->
            @$el.show()

        unload: ->
            @$el.hide()
