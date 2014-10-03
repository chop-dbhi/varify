/* global define */

define([
    'jquery',
    'underscore',
    'cilantro',
    'cilantro/ui/numbers',
    '../tables',
    '../../utils'
], function($, _, c, numbers, tables, utils) {

    var ResultCount = c.ui.ResultCount.extend({
        initialize: function() {
            this.data = {};

            if (!(this.data.context = this.options.context)) {
                throw new Error('context model required');
            }

            if (!(this.data.samples = this.options.samples)) {
                throw new Error('samples collection required');
            }

            this.listenTo(this.data.samples, 'sync', this.renderLabel);
        },

        renderCount: function(model, count) {
            numbers.renderCount(this.ui.count, count);

            this.renderLabel();
        },

        renderLabel: function() {
            var samples = utils.samplesInContext(this.data.context, this.data.samples);

            if (samples.length === 0) {
                this.ui.label.text('records in unknown sample');
                this.ui.label.attr('title', 'Unknown Sample');
                this.ui.label.tooltip('destroy');
            }
            else if (samples.length === 1) {
                this.ui.label.text('records in ' + samples[0]);
                this.ui.label.attr('title', samples[0]);
                this.ui.label.tooltip({
                    animation: false,
                    html: true,
                    placement: 'bottom',
                    container: 'body'
                });
            }
            else {
                this.ui.label.text('records in various samples');
                this.ui.label.attr('title', 'Various Samples');
                this.ui.label.tooltip('destroy');
            }
        }
    });

    // Extend the default Cilantro results workflow to account for items like
    // our custom result table and the integration of phenotype data.
    var ResultsWorkflow = c.ui.ResultsWorkflow.extend({
        template: 'varify/workflows/results',

        events: function() {
            return _.extend({
                'click [data-toggle=phenotype-dialog]': 'showPhenotypesModal'
            }, c.ui.ResultsWorkflow.prototype.events);
        },

        initialize: function() {
            _.bindAll(this, 'hideLoadingOverlay');

            c.ui.ResultsWorkflow.prototype.initialize.call(this);

            // We will manage the hiding of the loading overlay ourselves. The
            // call to the preview endpoint returns the variant IDs. The actual
            // variant data is retrieved by another call after the call to the
            // preview endpoint comes back so we cannot let Cilantro hide the
            // overlay after the preview endpoint syncs like it normally does.
            // Insted, we need to hide it after the variant collection becomes
            // synced.
            this.stopListening(this.data.results, 'sync');

            // The Cilantro workflow no longer requires the context but we
            // need it to have any hope of referencing the sample name in the
            // result count. The data object will already have been initialized
            // in the call above so we are safe to add the context onto it
            // here.
            if (!(this.data.context = this.options.context)) {
                throw new Error('context model required');
            }

            if (!(this.data.samples = this.options.samples)) {
                throw new Error('samples collection required');
            }
        },

        showPhenotypesModal: function() {
            c.dialogs.phenotype.open();
        },

        onRender: function() {
            $(document).on('scroll', this.onPageScroll);

            this.paginator.show(new c.ui.Paginator({
                model: this.data.results
            }));

            this.count.show(new ResultCount({
                model: this.data.results,
                context: this.data.context,
                samples: this.data.samples
            }));

            this.table.show(new tables.ResultTable({
                view: this.data.view,
                collection: this.data.results
            }));
            // When the body of the table reports that it is synced, then the
            // variant data has arrived and we can now hide the loading
            // overlay.
            this.table.currentView.on('itemview:synced', this.hideLoadingOverlay);

            this.ui.navbarButtons.tooltip({
                animation: false,
                placement: 'bottom'
            });
        }

    });

    return {
        ResultsWorkflow: ResultsWorkflow
    };

});
