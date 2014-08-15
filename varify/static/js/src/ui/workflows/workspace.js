/* global define */

define([
    'cilantro',
    'marionette',
    '../sample'
], function(c, Marionette, sample) {


    var WorkspaceWorkflow = c.ui.WorkspaceWorkflow.extend({
        template: 'varify/workflows/workspace',

        ui: {
            sampleVariantSetHelp: '[data-target=sample-variant-set-help]',
            createVariantSetButton: '[data-target=create-variant-set]'
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
        },

        onSampleSelected: function(model) {
            this.sample = model;
            this.renderSampleDetail();
            this.renderSampleVariantSets();
        },

        renderSampleDetail: function() {
            var sampleDetail = new this.regionViews.sampleDetail({
                model: this.sample
            });

            this.sampleDetail.show(sampleDetail);
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
