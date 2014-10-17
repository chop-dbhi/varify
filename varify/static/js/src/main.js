/* global require */

require({
    config: {
        tpl: {
            variable: 'data'
        }
    },
    shim: {
        bootstrap: ['jquery'],
        marionette: {
            deps: ['backbone'],
            exports: 'Marionette'
        },
        highcharts: {
            deps: ['jquery'],
            exports: 'Highcharts'
        }
    }
}, [
    'jquery',
    'underscore',
    'cilantro',
    'varify/ui',
    'varify/models',
    'varify/csrf'
], function($, _, c, ui, models) {

    var SAMPLE_CONCEPT_ID = 2,
        SAMPLE_FIELD_ID = 111;

    // Add namespaced variables for reference in other modules
    c.config.set('varify.sample.concept', SAMPLE_CONCEPT_ID);
    c.config.set('varify.sample.field', SAMPLE_FIELD_ID);

    // Session options
    var options = {
        url: c.config.get('url'),
        credentials: c.config.get('credentials')
    };

    var augmentFixedView = function() {
        var newView = {
            view: {
                columns: [SAMPLE_CONCEPT_ID]
            }
        };

        var json;
        if (c.session && (json = c.session.data.views.session.get('json'))) {
            newView.view.ordering = json.ordering;
        }

        return newView;
    };

    // Globally disable stats on all fields
    c.config.set('fields.defaults.form.stats', false);

    // Disable charts for all the types they are enabled for in the default
    // Cilantro config.
    c.config.set('fields.types.number.form.chart', false);
    c.config.set('fields.types.date.form.chart', false);
    c.config.set('fields.types.time.form.chart', false);
    c.config.set('fields.types.datetime.form.chart', false);

    // Convert the Chromosome, Effect, Effect Region, Effect Impact, and
    // Functional Class fields to be multi-selection drop down lists.
    c.config.set('fields.instances.27.form.controls', ['multiSelectionList']);
    c.config.set('fields.instances.28.form.controls', ['multiSelectionList']);
    c.config.set('fields.instances.29.form.controls', ['multiSelectionList']);
    c.config.set('fields.instances.61.form.controls', ['multiSelectionList']);
    c.config.set('fields.instances.64.form.controls', ['multiSelectionList']);

    // Force the Cohort field to use the built-in search control.
    c.config.set('fields.instances.75.form.controls', ['search']);

    // Convert the Genotype field to be a single selection drop down.
    c.config.set('fields.instances.68.form.controls', ['singleSelectionList']);

    // Set the custom control for the Sift and PolyPhen2 fields.
    c.controls.set('Sift', ui.SiftSelector);
    c.controls.set('PolyPhen', ui.PolyPhenSelector);
    c.config.set('fields.instances.58.form.controls', ['Sift']);
    c.config.set('fields.instances.56.form.controls', ['PolyPhen']);

    // Use a NullSelector control for the HGMD field with custom labels
    // defined for the options.
    c.config.set('fields.instances.110.form.controls', [{
        options: {
            'isNullLabel': 'Not In HGMD',
            'isNotNullLabel': 'In HGMD'
        },
        control: 'nullSelector'
    }]);

    // If no sample is selected, open the dialog to select one
    var showSampleDialog = function(required) {
        if (_.findWhere(required, {concept: SAMPLE_CONCEPT_ID})) {
            c.dialogs.sample.open();
        }
    };

    // Use sample dialog as means of selecting the sample
    c.on(c.CONCEPT_FOCUS, function(concept) {
        if (concept === SAMPLE_CONCEPT_ID) {
            c.dialogs.sample.open();
        }
    });

    // Mark the Sample concept as required and display a notification to the
    // user when it is not populated.
    c.config.set('filters.required', [{concept: SAMPLE_CONCEPT_ID}]);
    c.on(c.CONTEXT_INVALID, showSampleDialog);
    c.on(c.CONTEXT_REQUIRED, showSampleDialog);

    // Open the default session when Cilantro is ready
    c.ready(function() {

        // Open the default session defined in the pre-defined configuration.
        // Initialize routes once data is confirmed to be available
        c.sessions.open(options).then(function() {

            // Force calls to the preview endpoint to use a fixed view composed solely
            // of the sample concept. This will have the intended result of removing
            // "duplicate" rows in the results table that sometimes occured due to
            // the user's view.
            c.config.set('session.defaults.data.preview', augmentFixedView);

            // Add additional data to the session
            this.data.samples = new models.Samples();
            this.data.samples.fetch({reset: true});

            // Ensure the session context is valid
            this.data.contexts.once('sync', function() {
                this.session.validate();
            });

            // Panels are defined in their own namespace since they shared
            // across workflows
            c.panels = {
                concept: new c.ui.ConceptPanel({
                    collection: this.data.concepts.queryable
                }),

                context: new c.ui.ContextPanel({
                    model: this.data.contexts.session
                })
            };

            c.dialogs = {
                exporter: new ui.ExporterDialog({
                    // TODO rename data.exporter on session
                    exporters: this.data.exporter
                }),

                columns: new c.ui.ConceptColumnsDialog({
                    view: this.data.views.session,
                    concepts: this.data.concepts.viewable
                }),

                query: new c.ui.EditQueryDialog({
                    view: this.data.views.session,
                    context: this.data.contexts.session,
                    collection: this.data.queries
                }),

                deleteQuery: new c.ui.DeleteQueryDialog(),

                resultDetails: new ui.ResultDetailsModal(),

                phenotype: new ui.Phenotype({
                    context: this.data.contexts.session,
                    samples: this.data.samples
                }),

                sample: new ui.SampleDialog({
                    context: this.data.contexts.session,
                    samples: this.data.samples
                }),

                variantSet: new ui.VariantSetDialog()
            };

            var elements = [];

            // Render and append panels in the designated main element
            // prior to starting the session and loading the initial workflow
            // Render and append element for insertion
            $.each(c.panels, function(key, view) {
                view.render();
                elements.push(view.el);
            });

            $.each(c.dialogs, function(key, view) {
                view.render();
                elements.push(view.el);
            });

            // Set the initial HTML with all the global views
            var main = $(c.config.get('main'));
            main.append.apply(main, elements);

            c.workflows = {
                workspace: new ui.WorkspaceWorkflow({
                    queries: this.data.queries,
                    context: this.data.contexts.session,
                    view: this.data.views.session,
                    public_queries: this.data.public_queries,   // jshint ignore:line
                    samples: this.data.samples,
                    stats: this.data.stats
                }),

                query: new c.ui.QueryWorkflow({
                    context: this.data.contexts.session,
                    concepts: this.data.concepts.queryable
                }),

                results: new ui.ResultsWorkflow({
                    view: this.data.views.session,
                    // We need the context in the results workflow because we
                    // need to be able to reference the sample name.
                    context: this.data.contexts.session,
                    results: this.data.preview,
                    samples: this.data.samples
                }),

                sampleload: new ui.SampleLoader({
                    context: this.data.contexts.session
                }),

                queryload: new c.ui.QueryLoader({
                    queries: this.data.queries,
                    context: this.data.contexts.session,
                    view: this.data.views.session
                }),

                variantset: new ui.VariantSetWorkflow()
            };

            // Define routes
            var routes = [{
                id: 'workspace',
                route: 'workspace/',
                view: c.workflows.workspace
            }, {
                id: 'query',
                route: 'query/',
                view: c.workflows.query
            }, {
                id: 'results',
                route: 'results/',
                view: c.workflows.results
            }, {
                id: 'sample-load',
                route: 'sample/:sample_id/',
                view: c.workflows.sampleload
            }, {
                id: 'query-load',
                route: 'results/:query_id/',
                view: c.workflows.queryload
            }, {
                id: 'variant-set',
                route: 'variant-sets/:variant_set_id',
                view: c.workflows.variantset
            }];

            // Register routes and start the session
            this.start(routes);
        });

    });

});
