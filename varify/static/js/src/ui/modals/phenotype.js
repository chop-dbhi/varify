/* global define */

define([
    'underscore',
    'backbone',
    'marionette',
    './phenotype/diagnoses',
    './phenotype/annotations',
    '../../models',
    '../../utils'
], function(_, Backbone, Marionette, diagnoses, annotations, models, utils) {

    var Phenotype = Marionette.Layout.extend({
        className: 'modal hide',

        template: 'varify/modals/phenotype',

        ui: {
            closeButton: '[data-target=close-phenotypes]',
            content: '[data-target=content]',
            personalInfo: '[data-target=personal-info]',
            error: '[data-target=error]',
            notes: '[data-target=notes]',
            pedigree: '[data-target=pedigree]',
            headerLabel: '[data-target=header-label]',
            loading: '[data-target=loading]',
            thumbnail: '[data-target=thumbnail]',
            recalculateButton: '[data-target=recalculate]',
            warning: '[data-target=warning]',
            hideOnRetrieve: '[data-action=hide-on-retrieve]'
        },

        regions: {
            confirmedDiagnoses: '[data-target=confirmed-diagnoses]',
            suspectedDiagnoses: '[data-target=suspected-diagnoses]',
            ruledOutDiagnoses: '[data-target=ruled-out-diagnoses]',
            annotations: '[data-target=annotations]'
        },

        events: {
            'click @ui.closeButton': 'close',
            'click @ui.recalculateButton': 'recalculate'
        },

        alerts: {
            missingSample: 'The phenotypes cannot be retrieved because ' +
                           'there is not any sample selected. To select a ' +
                           'sample, navigate to the Query page and open the ' +
                           'Sample concept(under the Proband header). From ' +
                           'this control, you can use the +/- buttons to ' +
                           'add a sample to the list or enter a label ' +
                           'directly in the text box. Once you have ' +
                           'selected a sample, click the &quot;Apply ' +
                           'Filter&quot; button and then return to this ' +
                           'page and reopen this window to retrieve the ' +
                           'phenotypes.',
            multipleSamples: 'The phenotypes cannot be retrieved because ' +
                             'there are multiple samples selected. To fix ' +
                             'this, navigate to the Query page and open the ' +
                             'Sample concept(under the Proband header). ' +
                             'From this control you can remove samples ' +
                             'directly from the text box or using the - ' +
                             'buttons. Once you have limited the set to a ' +
                             'singe sample, click the &quot;Update Filter' +
                             'button and then return to this page and ' +
                             'reopen this window to retrieve the phenotypes'
        },

        initialize: function() {
            this.data = {};

            _.bindAll(this, 'onFetchError');

            if (!(this.data.context = this.options.context)) {
                throw new Error('context model required');
            }
        },

        renderNotes: function(notes) {
            var html = [];

            html.push('<div class=span6>');
            html.push('<h6>Notes:</h6>');

            if (notes && notes.length) {
                html.push('<p>' + notes[0].note);
            }
            else {
                html.push('<span class=muted>No notes</span>');
            }

            return html.join('');
        },

        onFetchError: function() {
            delete this.request;

            this.ui.loading.hide();
            this.ui.error.html('There was an error retrieving the phenotypes.').show();
        },

        recalculate: function() {
            this.retrievePhenotypes(true);
        },

        onRender: function(){
            delete this.request;

            this.ui.recalculateButton.prop('disabled', false);
            this.ui.loading.hide();

            // Initially, the model is not set to anything. It is only after the
            // request for the phenotype is successful that we have a model.
            if (!this.model) return;


            // Render each region
            this.annotations.show(new annotations.Annotations({
                name: "HPO Annotations",
                collection: new Backbone.Collection(this.model.get('hpoAnnotations')),
            }));

            this.confirmedDiagnoses.show(new diagnoses.Diagnoses({
                name: 'Confirmed Diagnoses',
                collection: new Backbone.Collection(this.model.get('confirmedDiagnoses'))
            }));

            this.suspectedDiagnoses.show(new diagnoses.Diagnoses({
                name: 'Suspected Diagnoses',
                collection: new Backbone.Collection(this.model.get('suspectedDiagnoses')),
            }));

            this.ruledOutDiagnoses.show(new diagnoses.Diagnoses({
                name: 'Ruled Out Diagnoses',
                collection: new Backbone.Collection(this.model.get('ruledOutDiagnoses')),
            }));

            this.ui.notes.html(this.renderNotes(this.model.get('notes')));

            if (!this.model.get('pedigree')) {
                this.ui.pedigree.hide();
                this.ui.thumbnail.hide();
            }

            this.ui.content.show();
        },

        retrievePhenotypes: function(recalculateRankings) {
            if (recalculateRankings === null) {
                recalculateRankings = false;
            }

            // We are about to attempt to reload the phenotypes so we want to
            // start fresh and clear any old artifacts.
            this.ui.hideOnRetrieve.hide();
            this.ui.recalculateButton.prop('disabled', true);

            var samples = utils.samplesInContext(this.data.context);

            // If there aren't exactly 1 samples in the current context then
            // warn the user with instructions on limiting their filter to
            // a single sample. The phenotypes endpoint does not support multi-
            // sample phenotype lookups.
            if (samples.length === 1) {
                this.ui.headerLabel.text('Phenotypes for ' + samples[0]);

                // Show the loading indicator before making the request.
                this.ui.loading.show();

                var phenotype = new models.Phenotype({
                    sampleId: samples[0]
                });

                var _this = this;
                this.request = phenotype.fetch({
                    data: {
                        recalculate_rankings: recalculateRankings   // jshint ignore: line
                    },
                    processData: true,
                    success: function(model) {
                        // Set the the model so that the serializeData function
                        // has access to the attributes.
                        _this.model = model;
                        _this.render();
                        _this.ui.headerLabel.text('Phenotypes for ' + samples[0]);
                    },
                    error: this.onFetchError
                });
            }
            else {
                this.ui.headerLabel.text('Phenotypes');

                if (samples.length === 0) {
                    this.ui.error.html(this.alerts.missingSample);
                }
                else {
                    this.ui.error.html(this.alerts.multipleSamples).show();
                }
            }
        },

        open: function() {
            this.retrievePhenotypes();
            this.$el.modal('show');
        },

        close: function() {
            if (this.request) {
                this.request.abort();
                delete this.request;
            }

            this.$el.modal('hide');
        }
    });

    return {
        Phenotype: Phenotype
    };

});
