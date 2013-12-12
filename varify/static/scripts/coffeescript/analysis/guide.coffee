define [
    'environ'
    'mediator'
    'jquery'
    'underscore'
    'router'
    'app/controls'
    'app/analysis/controls'
    'serrano'
], (environ, mediator, $, _, Router, Controls, Analysis, Serrano) ->

    data = @probandData

    analysisModal = $ '#analysis-modal'
    analysisModal.on 'submit', '.modal-body form', false

    # Proband
    probandSection = $ '#analysis-proband'
    summarySection = $ '#analysis-summary'

    $projects = probandSection.find('[name=project]')
    $batches = probandSection.find('[name=batch]')
    $samples = probandSection.find('[name=sample]')

    $placeholder = $('<option>').attr('value', '').text('---')

    # Add placeholders
    $projects.append $placeholder.clone()
    $batches.append $placeholder.clone()
    $samples.append $placeholder.clone()

    projects = {}
    samples = {}

    for sample in data
        # Always populate the Projects
        if not (project = projects[sample.project])
            $projects.append '<option value="' + sample.project + '">' + sample.project + '</option>'
            project = projects[sample.project] = {}

        # Batch populate based on the project selection
        if not (batch = project[sample.batch])
            batch = project[sample.batch] = []

        batch.push sample.id
        # Used for populating existing values
        samples[sample.id] = sample

    $projects.on 'change', (event) ->
        # Empty dependent elements
        $batches.html $placeholder.clone()
        $samples.html $placeholder.clone()
        batches = projects[$projects.val()]
        for key of batches
            $batches.append '<option value="' + key + '">' + key + '</option>'

    $batches.on 'change', (event) ->
        # Empty dependent elements
        $samples.html $placeholder.clone()
        batchSamples = projects[$projects.val()][$batches.val()]
        for id in batchSamples
            $samples.append '<option value="' + id + '">' + samples[id].sample + '</option>'

    $samples.on 'change', (event) ->
        mediator.publish(
            'analysis/sample/change',
            $samples.val(),
            $samples.find(':selected').text())

        if $samples.val()
            probandError.hide()
        else
            probandError.show()
            event.stopImmediatePropagation()

    # Find all elements that represent a functional aspect to building
    # up the datacontext node
    nodeControls = analysisModal.find '[data-id]'

    # Custom control classes
    nodeControlClasses =
        58: Analysis.SiftControl
        56: Analysis.PolyPhen2Control
        37: Analysis.PercentControl
        51: Analysis.PercentControl
        104: Analysis.CohortAFControl
        8: Analysis.OtherOptionControl
        9: Analysis.OtherOptionControl
        86: Analysis.TypeaheadControl
        69: Analysis.RangeControl

    setTabEnabled = (isEnabled) ->
        # Get the currently selected tab
        activeTab = analysisModal.find('.tab-pane.active')

        # Set the disabled state of all the user input elements and add or
        # remove a blocking click handler to the tab items based on the
        # value of isEnabled. This is because the <a> tag doesn't respect the
        # disabled attribute so we need to manually prevent the user from
        # switching tabs until the context update completes.
        tabItemLinks = analysisModal.find('.nav-tabs > li > a')

        if isEnabled
            activeTab.find('input').removeAttr('disabled')
            activeTab.find('select').removeAttr('disabled')
            tabItemLinks.css('cursor', 'auto')
            tabItemLinks.removeClass('muted')
            tabItemLinks.off 'click'
        else
            activeTab.find('input').attr('disabled', true)
            activeTab.find('select').attr('disabled', true)
            tabItemLinks.css('cursor', 'default')
            tabItemLinks.addClass('muted')
            tabItemLinks.on 'click', (event) ->
                event.preventDefault()
                return false

    # When the data context is being saved, block all input until we get the
    # concept back
    mediator.subscribe Serrano.DATACONTEXT_SYNCING, (model) =>
        $('.tab-pane.active').addClass('loading')
        setTabEnabled(false)

    mediator.subscribe Serrano.DATACONTEXT_SYNCED, (model) =>
        $('.tab-pane.active').removeClass('loading')
        setTabEnabled(true)

        if not model.isSession() then return

        conditions = $('#analysis-conditions').html('')
        json = model.get('json')
        if not json
            conditions.append "<li>No filters are applied</li>"
        else if json.children
            for obj in json.children
                if obj then conditions.append "<li>#{ obj.language }</li>"
            return
        else if json.language
            conditions.append "<li>#{ json.language }</li>"

    # When the data context is cleared, the analysis modal form controls need
    # to be reset to their default values
    mediator.subscribe Serrano.DATACONTEXT_CLEAR, () =>
        analysisModal.find('select').val('')
        analysisModal.find('input[type=text]').val('')

    initControls = (tree) ->
        views = {}

        for control in nodeControls
            control = $ control
            id = control.data 'id'

            # Use an existing node from the datacontext, otherwise create
            # a new one
            if not (model = tree.getNodes(id)[0])
                model = new Serrano.DataContextNode

            # Check if there is a custom control class, otherwise use the
            # default.
            if not (klass = nodeControlClasses[id])
                klass = Controls.DataContextNode

            if id is 86
                geneSearchTimer = null
                control.find('[data-value]').typeahead
                    source: (query, typeahead) ->
                        clearTimeout geneSearchTimer
                        geneSearchTimer = setTimeout ->
                            Backbone.ajax
                                url: environ.absolutePath '/api/genes/'
                                data: query: query
                                success: (resp) ->
                                    if (!resp.results)
                                        if typeahead.shown then typeahead.hide()
                                    typeahead.render(resp.results.slice(0, typeahead.options.items)).show()
                        , 300

                    mode: 'multiple'
                    renderItem: (i, item) ->
                        $("<li data-value=\"#{ item.symbol }\"><a href=#><strong>#{ item.symbol }</strong> - #{ item.name }</a></li>")[0]

            view = new klass el: control, model: model

            # Proband
            if id is 2 and model.id
                # If selectedProband is set then we will be setting the proband
                # info later so we can ignore this step.
                if (sample = samples[model.get 'value']) and _(selectedProband).isEmpty()
                    $projects.val(sample.project).change()
                    $batches.val(sample.batch).change()
                    $samples.val(sample.id).change()

            views[id] = view

        # If there was proband information parsed out of the url then start the
        # process of selecting that proband and showing this modal.
        if not _.isEmpty(selectedProband)
            $projects.val(selectedProband.project).change()
            $batches.val(selectedProband.batch).change()

            if selectedProband.sample?
                # Since the sample is referenced in the url by name and the
                # options use sample id for their values, we need to look the
                # sample up by matching the name with the text in the dropdown.
                $('select[name=sample] option').filter(() ->
                    return $(this).text() == selectedProband.sample
                ).prop('selected', true)
                $samples.change()

            analysisModal.modal('show')
            analysisModal.find('[href=#analysis-0]').tab('show')

        return

    # Subscribe for for only a single publish..
    mediator.subscribe Serrano.DATACONTEXT_SYNCED, initControls, true

    probandError = $('#proband-required-error').hide()

    # Add handler to catch "Close" button click event. This handle just closes the analysis modal dialog.
    $('#close-analysis').on 'click', (event) =>
        event.preventDefault()

        analysisModal.modal('hide')


    # Add handler to catch "Save" button and check for a proband
    $('#save-analysis').on 'click', (event) ->
        event.preventDefault()

        if $samples.val()
            analysisModal.modal('hide')
            Router.navigate 'review/', trigger: true
        else
            analysisModal.find('[href=#analysis-0]').tab('show')
            probandError.show()
