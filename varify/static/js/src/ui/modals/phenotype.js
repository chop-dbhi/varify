/* global define */

define([
    'underscore',
    'marionette',
    '../../models',
    '../../utils'
], function(_, Marionette, models, utils) {

    var Phenotype = Marionette.ItemView.extend({
        className: 'modal hide',

        template: 'varify/modals/phenotype',

        ui: {
            annotations: '[data-target=annotations]',
            closeButton: '[data-target=close-phenotypes]',
            content: '[data-target=content]',
            diagnoses: '[data-target=diagnoses]',
            error: '[data-target=error]',
            headerLabel: '[data-target=header-label]',
            loading: '[data-target=loading]',
            notes: '[data-target=notes]',
            pedigree: '[data-target=pedigree]',
            recalculateButton: '[data-target=recalculate]',
            updateTimes: '[data-target=update-times]',
            warning: '[data-target=warning]',
            hideOnRetrieve: '[data-action=hide-on-retrieve]'
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

            _.bindAll(this, 'onFetchError', 'onFetchSuccess');

            if (!(this.data.context = this.options.context)) {
                throw new Error('context model required');
            }
        },

        renderHPO: function(annotations) {
            var html = [], key, priority;

            html.push('<div class=span6>');
            html.push('<h6>HPO:</h6>');

            if (annotations && annotations.length) {
                html.push('<ul>');

                for (key in annotations) {
                    html.push('<li>');

                    html.push('<a href="http://www.human-phenotype-ontology.org/hpoweb/showterm?id=' +  // jshint ignore: line
                              annotations[key].hpo_id + '" target="_blank">' +  // jshint ignore: line
                              annotations[key].name + '</a>');

                    if ((priority = annotations[key].priority)) {
                        html.push('<span class="badge badge-important">' +
                                  priority + '</span>');
                    }

                    html.push('</li>');
                }

                html.push('</ul>');
            }
            else {
                html.push('<span class=muted>No HPO annotations</span>');
            }

            html.push('</div>');

            return html.join('');
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

        _renderDiagnoses: function(diagnoses) {
            if (diagnoses && diagnoses.length) {
                var html = [], key;

                html.push('<ul>');

                for (key in diagnoses) {
                    html.push('<li>');
                    html.push('<a href="http://purl.bioontology.org/ontology/OMIM/' +
                              diagnoses[key].omim_id + '" target="_blank">' +   // jshint ignore: line
                              diagnoses[key].name + '</a>');

                    if (diagnoses[key].priority) {
                        html.push('<span class="badge badge-important">' +
                                  diagnoses[key].priority + '</span>');
                    }

                    html.push('</li>');
                }

                html.push('</ul>');

                return html.join('');
            }
            else {
                return '<span class=muted>No diagnoses</span>';
            }
        },

        renderDiagnoses: function(attr) {
            var html = [];

            html.push('<div class=span4>');
            html.push('<h6>Confirmed Diagnoses:</h6>');
            html.push(this._renderDiagnoses(attr.confirmedDiagnoses));
            html.push('</div>');

            html.push('<div class=span4>');
            html.push('<h6>Suspected Diagnoses:</h6>');
            html.push(this._renderDiagnoses(attr.suspectedDiagnoses));
            html.push('</div>');

            html.push('<div class=span4>');
            html.push('<h6>Ruled Out Diagnoses:</h6>');
            html.push(this._renderDiagnoses(attr.ruledOutDiagnoses));
            html.push('</div>');

            return html.join('');
        },

        renderUpdateTimes: function(attr) {
            var html = [];

            html.push('<div class=span6>');
            html.push('<h6>Phenotypes Updated: </h6>' + attr.last_modified);    // jshint ignore: line
            html.push('</div>');

            html.push('<div class=span6>');
            html.push('<h6>Rankings Updated: </h6>' + attr.phenotype_modified); // jshint ignore: line
            html.push('</div>');

            return html.join('');
        },

        onFetchSuccess: function(model) {
            delete this.request;

            this.ui.recalculateButton.prop('disabled', false);
            this.ui.loading.hide();

            var attr = model.attributes;

            this.ui.annotations.html(this.renderHPO(attr.hpoAnnotations));
            this.ui.notes.html(this.renderNotes(attr.notes));
            this.ui.diagnoses.html(this.renderDiagnoses(attr));
            this.ui.updateTimes.html(this.renderUpdateTimes(attr));

            if (attr.pedigree) {
                this.ui.pedigree.attr('href', attr.pedigree);
                this.ui.pedigree.show();
            }
            else {
                this.ui.pedigree.hide();
            }

            this.ui.content.show();
        },

        onFetchError: function() {
            delete this.request;

            this.ui.loading.hide();
            this.ui.error.html('There was an error retrieving the phenotypes.');
            this.ui.error.show();
        },

        recalculate: function() {
            this.retrievePhenotypes(true);
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
                        _this.onFetchSuccess(model);
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
                    this.ui.error.html(this.alerts.multipleSamples);
                }

                this.ui.error.show();
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
