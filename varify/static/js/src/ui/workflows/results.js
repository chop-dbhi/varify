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
        },

        renderCount: function(model, count) {
            var samples = utils.samplesInContext(this.data.context);

            numbers.renderCount(this.ui.count, count);
            if (samples.length === 1) {
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
                this.ui.label.attr('title', 'various samples');
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
            c.ui.ResultsWorkflow.prototype.initialize.call(this);

            // The Cilantro workflow no longer requires the context but we
            // need it to have any hope of referencing the sample name in the
            // result count. The data object will already have been initialized
            // in the call above so we are safe to add the context onto it
            // here.
            if (!(this.data.context = this.options.context)) {
                throw new Error('context model required');
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
                context: this.data.context
            }));

            this.table.show(new tables.ResultTable({
                view: this.data.view,
                collection: this.data.results
            }));


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
