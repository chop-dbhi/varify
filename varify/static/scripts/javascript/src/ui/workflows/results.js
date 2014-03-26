/* global define */

define([
    'underscore',
    'cilantro'
], function(_, c) {

    // Until support for multi-sample filters is removed, we need to override
    // the renderCount method to account for the possibility of multiple
    // sample names in the current context.
    var ResutlCount = c.ui.ResultCount.extend({
        renderCount: function(model, count, options) {
             var json, sample = null;

            if ((this.data.context != null) && ((json = this.data.context.get('json')) != null)) {
                _.each(json.children, function(child) {
                    if ((child.concept != null) && child.concept === 2) {
                        sample = child.children[0].value[0].label;
                    }
                });
            }

            numbers.renderCount(this.ui.count, count);
            this.ui.label.text("records in " + (sample || "various samples"));
            this.ui.label.attr('title', sample);

            if (sample != null) {
                this.ui.label.tooltip({
                    animation: false,
                    html: true,
                    placement: 'bottom',
                    container: 'body'
                });
            }
            else {
                this.ui.label.tooltip('destroy');
            }
        }
    });

    // Extend the default Cilantro results workflow to account for items like
    // our custom result table and the integration of phenotype data.
    var ResultsWorkflow = c.ui.ResultsWorkflow.extend({
        template: 'varify/workflows/results',

        _ui: {
            viewPhenotype: '.phenotype-modal .modal-body .span12',
            recalculateButton: '[data-target=recalculate-rankings]',
            phenotypeWarning: '[data-target=phenotype-warning]'
        },

        _events: {
            'click .export-options-modal [data-save]': 'onExportClicked',
            'click .export-options-modal [data-dismiss=modal]': 'onExportCloseClicked',
            'show.bs.modal .phenotype-modal': 'viewPhenotypesClicked',
            'hidden.bs.modal .phenotype-modal': 'hidePhenotypes',
            'click [data-target=recalculate-rankings]': 'recalculateRankingsClicked'
        },

        _regions: {
            resultDetailsModal: '.result-details-modal'
        },

        initialize: function() {
            // Extend ui, events, and regions on Cilantro ResultsWorkflow with
            // our local additions and register the row click listener before
            // calling initialize on parent.
            _.extend({}, this._ui, this.ui);
            _.extend({}, this._events, this.events);
            _.extend({}, this._regions, this.regions);

            c.on('resultRow:click', function(view, result) {
                this.resultDetailsModal.currentView.update(view, result);
            });

            c.ui.ResultsWorkflow.prototype.initialize.call(this);
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
    });

    return {
        ResultsWorkflow: ResultsWorkflow
    };

});
