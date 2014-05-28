/* global define */

define([
    'marionette'
], function(Marionette) {

    var VariantItem = Marionette.ItemView.extend({
        template: 'varify/workflows/variant-set/variant-item'
    });

    var VariantList = Marionette.CompositeView.extend({
        template: 'varify/workflows/variant-set/variant-list',

        itemView: VariantItem,

        itemViewContainer: '[data-target=items]'
    });

    var VariantDetails = Marionette.ItemView.extend({
        template: 'varify/workflows/variant-set/variant-details'
    });

    var KnowledgeCapture = Marionette.ItemView.extend({
        template: 'varify/workflows/variant-set/knowledge-capture'
    });

    var VariantSetWorkflow = Marionette.Layout.extend({
        className: 'variant-set-workflow row-fluid',

        template: 'varify/workflows/variant-set',

        regions: {
            variants: '.variant-list-region',
            variantDetails: '.variant-details-region',
            knowledgeCapture: '.knowledge-capture-region'
        },

        regionViews: {
            variants: VariantList,
            variantDetails: VariantDetails,
            knowledgeCapture: KnowledgeCapture
        },

        onRender: function() {
            this.variants.show(new this.regionViews.variants());

            this.variantDetails.show(new this.regionViews.variantDetails());

            this.knowledgeCapture.show(new this.regionViews.knowledgeCapture());
        }
    });

    return {
        VariantSetWorkflow: VariantSetWorkflow
    };

});
