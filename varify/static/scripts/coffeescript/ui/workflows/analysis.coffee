define [
    'cilantro'
    'underscore'
    'marionette'
    'tpl!templates/varify/workflows/analysis.html'
], (c, _, Marionette, templates...) ->

    templates = _.object ['analysis'], templates

    class AnalysisWorkflow extends Marionette.Layout
        className: 'analysis-workflow'

        template: templates.analysis

        ui:
            projects: 'select[name=project]'
            batches: 'select[name=batch]'
            samples: 'select[name=sample]'
            probandError: '#proband-required-error'

        events:
            'change select[name=project]': 'onProjectChange'
            'change select[name=batch]': 'onBatchChange'
            'change select[name=sample]': 'onSampleChange'

        initialize: ->
            @data = {}
            if not (@data.context = @options.context)
                throw new Error 'context model required'
            if not (@data.concepts = @options.concepts)
                throw new Error 'concept collection required'

            sampleUrl = window.location.href.replace("analysis/", "api/samples/")

            @sampleCollection = new c.models.Collection
            @sampleCollection.url = sampleUrl

        onRender: ->
            @$placeholder = $('<option>').attr('value', '').text('---')

            # Add placeholders
            @ui.projects.append @$placeholder.clone()
            @ui.batches.append @$placeholder.clone()
            @ui.samples.append @$placeholder.clone()

            @sampleCollection.fetch
                reset: true,
                success: @onSampleFetch,
                error: @onSampleFetchError

        onProjectChange: =>
            # Empty dependent elements
            @ui.batches.html @$placeholder.clone()
            @ui.samples.html @$placeholder.clone()
            @batches = @projects[@ui.projects.val()]
            for key of @batches
                @ui.batches.append '<option value="' + key + '">' + key + '</option>'

        onBatchChange: =>
            # Empty dependent elements
            @ui.samples.html @$placeholder.clone()
            batchSamples = @projects[@ui.projects.val()][@ui.batches.val()] or []
            for id in batchSamples
                @ui.samples.append '<option value="' + id + '">' + @samples[id].get('label') + '</option>'

        onSampleChange: (event) =>
            if @ui.samples.val()
                @ui.probandError.hide()
            else
                @ui.probandError.show()
                event.stopImmediatePropagation()

        onSampleFetch: (collection, response, options) =>
            @projects = {}
            @samples = {}

            for sample in @sampleCollection.models
                # Always populate the Projects
                if not (project = @projects[sample.get('project')])
                    @ui.projects.append '<option value="' + sample.get('project') + '">' + sample.get('project') + '</option>'
                    project = @projects[sample.get('project')] = {}

                # Batch populate based on the project selection
                if not (batch = project[sample.get('batch')])
                    batch = project[sample.get('batch')] = []

                batch.push sample.get('id')
                # Used for populating existing values
                @samples[sample.get('id')] = sample

        onSampleFetchError: (collection, response, options) =>
            console.log('Samples ERROR!')

    { AnalysisWorkflow }
