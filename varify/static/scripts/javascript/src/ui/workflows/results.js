/* global define */

define([
    'underscore',
    'cilantro',
    'cilantro/ui/numbers',
    '../tables'
], function(_, c, numbers, tables) {

    var ResultCount = c.ui.ResultCount.extend({
        initialize: function() {
            this.data = {};

            if (!(this.data.context = this.options.context)) {
                throw new Error('context model required');
            }
        },

        renderCount: function(model, count, options) {
            var samples = [], json;

            if (this.data.context  && (json = this.data.context.get('json'))) {
                _.each(json.children, function(child) {
                    if (child.concept && child.concept === 2) {
                        samples = _.pluck(child.children[0].value, 'label');
                    }
                });
            }

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

        _events: {
            'click .export-options-modal [data-save]': 'onExportClicked',
            'click .export-options-modal [data-dismiss=modal]': 'onExportCloseClicked',
            'click [data-toggle=phenotype-dialog]': 'showPhenotypesModal'
        },

        initialize: function() {
            this.events = _.extend({}, this._events, this.events);

            // This will be triggered by the table rows when they are clicked.
            c.on('resultRow:click', function(view, result) {
                c.dialogs.resultDetails.open(view, result);
            });

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

        onExportCloseClicked: function() {
            _.delay(function() {
                this.columns.currentView.resetFacets();
            }, 25);
        },

        onExportClicked: function() {
            // If there are no columns selected then we should not try to
            // export since the user will just get an empty file or empty
            // template. Show an error with instructions on adding a column.
            if (this.columns.currentView.data.facets.length === 0) {
                this.$('#export-error-message').html('One or more columns must be selected. Click the &quot;Columns&quot; tab, add at least one column using the green &quot;plus&quot; buttons next to the column names, and click &quot;Export&quot; to try again.');
                this.$('.export-options-modal .alert-block').show();
            }
            // Don't update the view if the columns haven't changed
            else if (_.isEqual(_.pluck(this.data.view.facets.models, 'id'),
                               _.pluck(this.columns.currentView.data.facets.models, 'id'))) {
                this.exportData();
            }
            else {
                this.data.view.facets.reset(this.columns.currentView.data.facets.toJSON());
                // TODO: Notify user if this fails
                this.data.view.save({}, {success: this.exportData});
            }
        },

        onRender: function() {
            $(document).on('scroll', this.onPageScroll);

            // Remove unsupported features from view/
            if (!c.isSupported('2.1.0')) {
                this.ui.saveQueryToggle.remove();
                this.ui.saveQuery.remove();
            }

            this.paginator.show(new c.ui.Paginator({
                model: this.data.results
            }));

            this.count.show(new ResultCount({
                model: this.data.results,
                context: this.data.context
            }));

            this.exportTypes.show(new c.ui.ExportTypeCollection({
                collection: this.data.exporters
            }));

            this.exportProgress.show(new c.ui.ExportProgressCollection({
                collection: this.data.exporters
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
