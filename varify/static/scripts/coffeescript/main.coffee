###
The 'main' script for bootstrapping the default Cilantro client. Projects can
use this directly or emulate the functionality in their own script.
###

require
    config:
        tpl:
            variable: 'data'

, [
    'cilantro',
    'project/ui',
    'project/csrf',
    'tpl!templates/varify/tables/header.html',
    'tpl!templates/varify/empty.html',
    'tpl!templates/varify/modals/result.html'
    'tpl!templates/varify/controls/hgmd.html'
    'tpl!templates/varify/controls/sift.html'
    'tpl!templates/varify/controls/polyphen.html'
], (c, ui, csrf, header, empty, result, hgmd, sift, polyphen) ->

    # Session options
    options =
        url: c.config.get('url')
        credentials: c.config.get('credentials')

    # Define custom templates
    c.templates.set('varify/tables/header', header)
    c.templates.set('varify/empty', empty)
    c.templates.set('varify/modals/result', result)
    c.templates.set('varify/controls/hgmd', hgmd)
    c.templates.set('varify/controls/sift', sift)
    c.templates.set('varify/controls/polyphen', polyphen)

    # Globally disable stats on all fields
    c.config.set('fields.defaults.form.stats', false)

    # Disable charts for all the types they are enabled for in the default
    # Cilantro config.
    c.config.set('fields.types.number.form.chart', false)
    c.config.set('fields.types.date.form.chart', false)
    c.config.set('fields.types.time.form.chart', false)
    c.config.set('fields.types.datetime.form.chart', false)

    # Convert the Chromosome, Effect, Effect Region, Effect Impact, and
    # Functional Class fields to be multi-selection drop down lists.
    c.config.set('fields.instances.27.form.controls', ['multiSelectionList'])
    c.config.set('fields.instances.28.form.controls', ['multiSelectionList'])
    c.config.set('fields.instances.29.form.controls', ['multiSelectionList'])
    c.config.set('fields.instances.61.form.controls', ['multiSelectionList'])
    c.config.set('fields.instances.64.form.controls', ['multiSelectionList'])

    c.config.set('fields.instances.75.form.controls', ['search'])

    # Convert the Genotype field to be a single selection drop down.
    c.config.set('fields.instances.68.form.controls', ['singleSelectionList'])

    # Set the custom control for the HGMD, Sift, and PolyPhen2 fields.
    c.controls.set('Hgmd', ui.HgmdSelector)
    c.controls.set('Sift', ui.SiftSelector)
    c.controls.set('PolyPhen', ui.PolyPhenSelector)
    c.config.set('fields.instances.110.form.controls', ['Hgmd'])
    c.config.set('fields.instances.58.form.controls', ['Sift'])
    c.config.set('fields.instances.56.form.controls', ['PolyPhen'])

    # A simple handler for CONTEXT_REQUIRED and CONTEXT_INVALID events that
    # tells the user which concept is required(when possible) or prints a
    # generic message in the case the concept name could not be found.
    notify_required = (concepts) =>
        # It is possible to update the configuration before a session
        # is opened so we only try to generate the concept names and notify
        # the user if there is any session data available for us to query.
        if not c.data?
            return

        names = _.map concepts || [], (concept) ->
            return c.data.concepts.get(concept.concept)?.get('name')

        # If we could not get the names of the required concepts then alter the
        # error message to be more generic
        if names
            message = 'The following concepts are required: ' + names.join(', ')
        else
            message = 'There are 1 or more required concepts'

        c.notify
            level: 'error',
            message: message

    # Mark the Sample concept as required and display a notification to the
    # user when it is not populated.
    c.config.set('query.concepts.required', [2])
    c.on c.CONTEXT_INVALID, notify_required
    c.on c.CONTEXT_REQUIRED, notify_required

    c.ready ->

        # Open the default session defined in the pre-defined configuration.
        # Initialize routes once data is confirmed to be available
        c.sessions.open(options).then ->

            # Define routes
            routes = [
               id: 'query'
               route: 'query/'
               view: new c.ui.QueryWorkflow
                   context: @data.contexts.session
                   concepts: @data.concepts.queryable
            ,
                id: 'results'
                route: 'results/'
                view: new ui.ResultsWorkflow
                    view: @data.views.session
                    context: @data.contexts.session
                    concepts: @data.concepts.viewable
                    # The differences in these names are noted
                    results: @data.preview
                    exporters: @data.exporter
                    queries: @data.queries
            ]

            # Query URLs supported as of 2.2.0
            if c.isSupported('2.2.0')
                routes.push
                    id: 'query-load'
                    route: 'results/:query_id/'
                    view: new c.ui.QueryLoader
                        queries: @data.queries
                        context: @data.contexts.session
                        view: @data.views.session

            # Workspace supported as of 2.1.0
            if c.isSupported('2.1.0')
                data =
                    queries: @data.queries
                    context: @data.contexts.session
                    view: @data.views.session

                # Public queries supported as of 2.2.0
                if c.isSupported('2.2.0')
                    data.public_queries = @data.public_queries

                routes.push
                    id: 'workspace'
                    route: 'workspace/'
                    view: new c.ui.WorkspaceWorkflow(data)

            # Register routes and start the session
            @start(routes)
