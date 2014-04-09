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
    'cilantro',
    'project/ui',
    'project/csrf',
    'tpl!../../templates/tables/header.html',
    'tpl!../../templates/modals/result.html',
    'tpl!../../templates/modals/phenotypes.html',
    'tpl!../../templates/controls/sift.html',
    'tpl!../../templates/controls/polyphen.html',
    'tpl!../../templates/workflows/results.html',
    'tpl!../../templates/export/dialog.html',
    'tpl!../../templates/sample/loader.html'
], function(c, ui, csrf, header, result, phenotype, sift, polyphen, results,
            exportDialog, sampleLoader) {

    // Session options
    var options = {
        url: c.config.get('url'),
        credentials: c.config.get('credentials')
    };

    var augmentFixedView = function() {
        var newView = {
            view: {
                columns: [2]
            }
        };

        var json;
        if ((json = c.session.data.views.session.get('json')) != null) {
            newView['view']['ordering'] = json['ordering'];
        }

        return newView;
    };

    // Define custom templates
    c.templates.set('varify/export/dialog', exportDialog);
    c.templates.set('varify/tables/header', header);
    c.templates.set('varify/modals/result', result);
    c.templates.set('varify/modals/phenotype', phenotype);
    c.templates.set('varify/controls/sift', sift);
    c.templates.set('varify/controls/polyphen', polyphen);
    c.templates.set('varify/workflows/results', results);
    c.templates.set('varify/sample/loader', sampleLoader);

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

    // Force calls to the preview endpoint to use a fixed view composed solely
    // of the sample concept. This will have the intended result of removing
    // "duplicate" rows in the results table that sometimes occured due to
    // the user's view.
    c.config.set('session.defaults.data.preview', augmentFixedView);

    // A simple handler for CONTEXT_REQUIRED and CONTEXT_INVALID events that
    // tells the user which concept is required(when possible) or prints a
    // generic message in the case the concept name could not be found.
    var notifyRequired = (function(_this) {
        return function(concepts) {
            if (c.data == null) return;

            var names = _.map(concepts || [], function(concept) {
                if ((currConcept = c.data.concepts.get(concept.concept)) != null) {
                    return currConcept.get('name');
                }
            });

            var message;
            if (names) {
                message = 'The following concepts are required: ' + names.join(', ');
            }
            else {
                message = 'There are 1 or more required concepts';
            }

            return c.notify({
                level: 'error',
                message: message
            });
        };
    })(this);

    // Mark the Sample concept as required and display a notification to the
    // user when it is not populated.
    c.config.set('query.concepts.required', [2]);
    c.on(c.CONTEXT_INVALID, notifyRequired);
    c.on(c.CONTEXT_REQUIRED, notifyRequired);

    // Open the default session when Cilantro is ready
    c.ready(function() {

        // Open the default session defined in the pre-defined configuration.
        // Initialize routes once data is confirmed to be available
        c.sessions.open(options).then(function() {

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

                resultDetails: new ui.ResultDetails,

                phenotype: new ui.Phenotype({
                    context: this.data.contexts.session
                })
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
                query: new c.ui.QueryWorkflow({
                    context: this.data.contexts.session,
                    concepts: this.data.concepts.queryable
                }),

                results: new ui.ResultsWorkflow({
                    view: this.data.views.session,
                    // We need the context in the results workflow because we
                    // need to be able to reference the sample name.
                    context: this.data.contexts.session,
                    results: this.data.preview
                }),

                sampleload: new ui.SampleLoader({
                    context: this.data.contexts.session
                })
            };

            // Define routes
            var routes = [{
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
            }];

            c.workflows.workspace = new c.ui.WorkspaceWorkflow({
                queries: this.data.queries,
                context: this.data.contexts.session,
                view: this.data.views.session,
                public_queries: this.data.public_queries
            });

            routes.push({
                id: 'workspace',
                route: 'workspace/',
                view: c.workflows.workspace
            });

            c.workflows.queryload = new c.ui.QueryLoader({
                queries: this.data.queries,
                context: this.data.contexts.session,
                view: this.data.views.session
            });

            routes.push({
                id: 'query-load',
                route: 'results/:query_id/',
                view: c.workflows.queryload
            });

            // Register routes and start the session
            this.start(routes);
        });

    });

});
