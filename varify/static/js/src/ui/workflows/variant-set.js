/* global define */

define([
    'jquery',
    'underscore',
    'backbone',
    'marionette',
    '../../models',
    '../../utils',
    '../result-details',
    'cilantro/utils/numbers'
], function($, _, Backbone, Marionette, models, utils, details, Numbers) {

    var VariantSet = Backbone.Model.extend({
        url: function() {
            // We know are are at <root_path>/variant-sets/<id> so we need
            // to strip off the variant-sets/<id> portion in order to
            // assemble the instance url to fetch the variant set.
            var instanceUrl = utils.toAbsolutePath('');
            instanceUrl = instanceUrl.replace(/variant-sets.*$/g, '');
            instanceUrl = instanceUrl + 'api/samples/variants/sets/' + this.id + '/';

            return instanceUrl;
        }
    });


    var EmptyVariantItem = Marionette.ItemView.extend({
        className: 'variant-item',

        tagName: 'li',

        template: 'varify/workflows/variant-set/empty-variant-item'
    });


    var VariantItem = Marionette.ItemView.extend({
        className: 'variant-item',

        tagName: 'li',

        template: 'varify/workflows/variant-set/variant-item',

        modelEvents: {
            'change:selected': 'onSelectedChange'
        },

        attributes: function() {
            return {
                'data-id': this.model.id
            };
        },

        templateHelpers: {
            getGeneSymbol: function() {
                var geneSymbol = '<span class=muted>unknown gene</span>';
                if (this.variant.unique_genes && this.variant.unique_genes.length) {    // jshint ignore:line
                    geneSymbol = this.variant.unique_genes[0];  // jshint ignore:line
                }

                return geneSymbol;
            },

            getHgvsP: function() {
                var hgvsp = '<span class=muted>N/A</span>';

                if (this.variant.effects && this.variant.effects.length) {
                    var effect = this.variant.effects[0];
                    hgvsp = (effect.hgvs_p || effect.amino_acid_change || hgvsp);   // jshint ignore:line
                }

                return hgvsp;
            },

            getHgvsC: function() {
                var hgvsc = '<span class=muted>N/A</span>';

                if (this.variant.effects && this.variant.effects.length) {
                    hgvsc = this.variant.effects[0].hgvs_c || hgvsc;    // jshint ignore:line
                }

                return hgvsc;
            },

            getAssessmentCount: function() {
                if (this.num_assessments) {     // jshint ignore:line
                    return '' + this.num_assessments + ' related assessments';      // jshint ignore:line
                }

                return '<span class=muted>This variant has not been assessed</span>';
            }
        },

        onSelectedChange: function() {
            this.$el.toggleClass('selected', this.model.get('selected'));
        },

        serializeData: function() {
            var data = this.model.toJSON();

            data.pchr = Numbers.toDelimitedNumber(data.variant.pos);

            return data;
        }
    });


    var VariantList = Marionette.CompositeView.extend({
        template: 'varify/workflows/variant-set/variant-list',

        itemView: VariantItem,

        itemViewContainer: '[data-target=items]',

        emptyView: EmptyVariantItem,

        events: {
            'click .variant-item': 'onClick'
        },

        onClick: function(event) {
            var id = $(event.currentTarget).data('id'),
                currentSelection = this.collection.findWhere({selected: true});

            // If the user clicks on the currently selected result then we
            // don't want to do anything.
            if (currentSelection && currentSelection.id === id) return;

            // Update the selected model and then
            this.collection.each(function(model) {
                if (model.id === id) {
                    model.set({selected: true});
                    currentSelection = model;
                }
                else {
                    model.set({selected: false});
                }
            });

            this.trigger('change:selection', currentSelection);
        }
    });


    var KnowledgeCapture = Marionette.ItemView.extend({
        template: 'varify/workflows/variant-set/knowledge-capture',

        ui: {
            form: 'form'
        },

        initialize: function(options) {
            this.data = {};

            if (options && options.result) {
                this.data.result = options.result;
            }
        },

        onRender: function() {
            if (this.data.result) {
                this.ui.form.show();
            }
        }
    });


    var VariantSetWorkflow = Marionette.Layout.extend({
        className: 'variant-set-workflow row-fluid',

        template: 'varify/workflows/variant-set',

        ui: {
            error: '[data-target=error-message]',
            loading: '[data-target=loading-message]',
            name: '[data-target=variant-set-name]',
            count: '[data-target=variant-set-count]',
            modified: '[data-target=variant-set-modified]',
            description: '[data-target=variant-set-description]'
        },

        regions: {
            variants: '.variant-list-region',
            variantDetails: '.variant-details-region',
            knowledgeCapture: '.knowledge-capture-region'
        },

        regionViews: {
            variants: VariantList,
            variantDetails: details.ResultDetails,
            knowledgeCapture: KnowledgeCapture
        },

        initialize: function() {
            _.bindAll(this, 'onChangeSelection', 'onFetchError',
                      'onFetchSuccess');

            this.on('router:load', this.onRouterLoad);
        },

        onChangeSelection: function(model) {
            var result = new models.Result(model.attributes, {parse: true});

            this.variantDetails.show(new this.regionViews.variantDetails({
                result: result
            }));

            this.knowledgeCapture.show(new this.regionViews.knowledgeCapture({
                result: result
            }));
        },

        onFetchError: function() {
            this.ui.loading.hide();

            this.showError('There was an error retrieving the variant set ' +
                           'from the server. Reload the page to try loading ' +
                           'the set again.');
        },

        onFetchSuccess: function(model) {
            this.ui.loading.hide();
            this.ui.error.hide();

            this.ui.name.text(model.get('name'));
            this.ui.count.text(model.get('count'));
            this.ui.modified.text(model.get('modified'));
            this.ui.description.text(model.get('description'));
            this.variants.currentView.collection.reset(model.get('results'));

            this.knowledgeCapture.show(new this.regionViews.knowledgeCapture());
        },

        onRender: function() {
            this.variants.show(new this.regionViews.variants({
                collection: new Backbone.Collection()
            }));
            this.variants.currentView.on('change:selection',
                                         this.onChangeSelection);
        },

        onRouterLoad: function(router, fragment, id) {
            var variantSetId = parseInt(id) || null;

            if (variantSetId) {
                this.variantSet = new VariantSet({
                    id: variantSetId
                });

                this.variantSet.fetch({
                    success: this.onFetchSuccess,
                    error: this.onFetchError
                });
            }
            else {
                this.showError('There was an issue parsing the variant set ' +
                               'ID. Try reloading the page or returning to the ' +
                               'Workspace page and clicking on the variant set ' +
                               'of interest again.');
            }
        },

        showError: function(errorHtml) {
            this.ui.error.show()
                .html('<div class="alert alert-error alert-block">' + errorHtml +
                      '</div>');
        }
    });


    return {
        VariantSetWorkflow: VariantSetWorkflow
    };

});
