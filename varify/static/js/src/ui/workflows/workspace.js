/* global define */

define([
    'underscore',
    'cilantro',
    'marionette',
    '../sample',
    '../../utils'
], function(_, c, Marionette, sample, utils) {


    var WorkspaceWorkflow = c.ui.WorkspaceWorkflow.extend({
        template: 'varify/workflows/workspace',

        ui: function() {
            return _.extend({
                sampleVariantSetHelp: '[data-target=sample-variant-set-help]',
                createVariantSetButton: '[data-target=create-variant-set]'
            }, c.ui.WorkspaceWorkflow.prototype.ui);
        },

        events: {
            'click @ui.createVariantSetButton': 'onCreateVariantSetClicked'
        },

        regions: {
            queries: '[data-target=query-region]',
            publicQueries: '[data-target=public-query-region]',
            sampleDetail: '[data-target=sample-details-region]',
            sampleVariantSets: '[data-target=sample-variant-sets-region]'
        },

        regionViews: {
            queries: c.ui.QueryList,
            publicQueries: c.ui.QueryList,
            sampleDetail: sample.SampleDetail,
            sampleVariantSets: sample.SampleVariantSets
        },

        initialize: function(options) {
            c.ui.WorkspaceWorkflow.prototype.initialize.call(this, options);

            if (!(this.data.samples = this.options.samples)) {
                throw new Error('samples collection required');
            }
        },

        onCreateVariantSetClicked: function() {
            c.dialogs.variantSet.open(this.sample);
        },

        onRender: function() {
            c.ui.WorkspaceWorkflow.prototype.onRender.call(this);

            this.ui.sampleVariantSetHelp.tooltip({
                title: 'A variant set is a fixed set of sample variants that ' +
                       'can be annotated and augmented at the creator\'s discretion.'
            });

            this.listenTo(this.data.samples, 'select', this.onSampleSelected);

            if (this.sample === undefined) {
                var contextSampleIds = utils.sampleIdsInContext(this.data.context);

                // If there are no samples in the context then don't bother
                // doing anything because the user will be forced to select
                // one and our select handler on this.data.samples will pick
                // up on it and take over from there.
                if (contextSampleIds.length > 0) {
                    // TODO: Given the rush to handle support multiple samples
                    // in the user context, I haven't had time to think through
                    // how variant set creation works when multiple samples are
                    // selected so, for now, just take the first and we will
                    // deal with this later.
                    this.sample = this.data.samples.get(contextSampleIds[0]);
                }
            }


            this.renderSampleDetail();
            this.renderSampleVariantSets();
        },

        onSampleSelected: function(model) {
            this.sample = model;
            this.renderSampleDetail();
            this.renderSampleVariantSets();
        },

        renderSampleDetail: function() {
            if (this.sample) {
                var sampleDetail = new this.regionViews.sampleDetail({
                    model: this.sample
                });

                this.sampleDetail.show(sampleDetail);
            }
        },

        renderSampleVariantSets: function() {
            if (!this.sample) return;

            var sampleVariantSets = new this.regionViews.sampleVariantSets({
                collection: this.sample.variantSets
            });

            // Fetch the variant sets for this sample
            this.sample.variantSets.fetch({reset: true});

            this.sampleVariantSets.show(sampleVariantSets);
        }
    });


    return {
        WorkspaceWorkflow: WorkspaceWorkflow
    };

});
