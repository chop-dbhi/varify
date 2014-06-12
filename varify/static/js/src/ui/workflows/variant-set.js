/* global define */

define([
    'jquery',
    'underscore',
    'backbone',
    'marionette',
    '../../models',
    '../../utils',
    '../result-details',
    'cilantro'
], function($, _, Backbone, Marionette, models, utils, details, c) {

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
                var count = '<span class=muted>This variant has not been assessed</span>';

                if (this.num_assessments) {     // jshint ignore:line
                    count = '' + this.num_assessments + ' related assessments';      // jshint ignore:line
                }

                return count;
            }
        },

        onSelectedChange: function() {
            this.$el.toggleClass('selected', this.model.get('selected'));
        },

        serializeData: function() {
            var data = this.model.toJSON();

            data.pchr = c.utils.toDelimitedNumber(data.variant.pos);

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
            form: 'form',
            errorMessage: '[data-target=error-message]',
            successMessage: '[data-target=success-message]',
            loading: '[data-target=loading]',
            pathogenicity: '[name=pathogenicity-radio]',
            category: '[name=category-radio]',
            motherResult: '[data-target=mother-result]',
            fatherResult: '[data-target=father-result]',
            evidenceDetails: '[data-target=evidence-details]',
            sangerRequested: '[name=sanger-radio]',
            saveButton: '[data-action=save]'
        },

        events: {
            'click @ui.saveButton': 'saveAssessment'
        },

        initialize: function() {
            _.bindAll(this, 'saveAssessment', 'onSaveError', 'onSaveSuccess',
                      'onFetchError', 'onFetchSuccess');
        },

        isValid: function() {
            var valid = true;

            this.ui.errorMessage.hide().html('');

            if (this.model.get('pathogenicity') === undefined) {
                valid = false;
                this.ui.errorMessage.append('<h5>Please select a pathogenicity.</h5>');
            }

            if (this.model.get('assessment_category') === undefined) {
                valid = false;
                this.ui.errorMessage.append('<h5>Please select a category.</h5>');
            }

            if (this.model.get('mother_result') === undefined) {
                valid = false;
                this.ui.errorMessage.append('<h5>Please select a result from ' +
                                            'the &quot;Mother&quot; dropdown.</h5>');
            }

            if (this.model.get('father_result') === undefined) {
                valid = false;
                this.ui.errorMessage.append('<h5>Please select a result from ' +
                                            'the &quot;Father&quot; dropdown.</h5>');
            }

            if (this.model.get('sanger_requested') === undefined) {
                valid = false;
                this.ui.errorMessage.append('<h5>Please select one of the ' +
                                            '&quot;Sanger Requested&quot; options.</h5>');
            }

            if (!valid) {
                this.ui.errorMessage.show();

                // Since the form is invalid, we jump to the top to show the
                // user the error(s).
                this.$el.parent().scrollTop(0);
            }

            return valid;
        },

        onFetchError: function() {
            this.ui.loading.hide();
            this.ui.form.hide();
            this.ui.errorMessage.show()
                .html('There was an error retrieving the assessment.');
        },

        onFetchSuccess: function() {
            this.ui.loading.hide();
            this.ui.errorMessage.hide();
            this.resetForm();
        },

        onRender: function() {
            if (!this.model) return;

            this.ui.errorMessage.hide();
            this.ui.successMessage.hide();

            // If this assessment already exists then fetch it, otherwise, we
            // can just show the form now.
            if (this.model.id) {
                this.ui.form.hide();
                this.ui.loading.show();

                this.model.fetch({
                    success: this.onFetchSuccess,
                    error: this.onFetchError
                });
            }
            else {
                this.ui.loading.hide();
                this.resetForm();
            }
        },

        onSaveError: function() {
            this.ui.errorMessage.show()
                .html('There was an error saving the assessment.');

            // Jump to the top to show the user the error.
            this.$el.parent().scrollTop(0);
        },

        onSaveSuccess: function() {
            this.ui.successMessage.show();

            // Jump to the top to show the user the message.
            this.$el.parent().scrollTop(0);
        },

        resetForm: function() {
            this.setRadioChecked('category-radio',
                                 this.model.get('assessment_category') || '1');
            this.setRadioChecked('pathogenicity-radio',
                                 this.model.get('pathogenicity') || '1');
            this.setRadioChecked('sanger-radio', this.model.get('sanger_requested'));

            this.ui.motherResult.val(this.model.get('mother_result'));
            this.ui.fatherResult.val(this.model.get('father_result'));
            this.ui.evidenceDetails.val(this.model.get('evidence_details'));

            this.ui.form.show();
        },

        saveAssessment: function() {
            this.model.set({
                evidence_details: this.ui.evidenceDetails.val(),    // jshint ignore:line
                sanger_requested: this.ui.sangerRequested.filter(':checked').val(),     // jshint ignore:line
                pathogenicity: parseInt(this.ui.pathogenicity.filter(':checked').val()),
                assessment_category: parseInt(this.ui.category.filter(':checked').val()),     // jshint ignore:line
                mother_result: parseInt(this.ui.motherResult.val()),  // jshint ignore:line
                father_result: parseInt(this.ui.fatherResult.val())   // jshint ignore:line
            });

            if (this.isValid()) {
                this.model.save(null, {
                    success: this.onSaveSuccess,
                    error: this.onSaveError
                });
            }
        },

        // Checks the radio button with the supplied name and value(all other
        // radios with that name are unchecked).
        setRadioChecked: function(name, value) {
            var checkedRadio, radios;

            // Lookup all the radio buttons using the supplied name
            radios = this.$el.find('input:radio[name=' + name + ']');
            // Uncheck any current selection
            radios.prop('checked', false);
            // Check the correct radio button based on the supplied value
            checkedRadio = radios.filter('[value=' + value + ']');
            checkedRadio.prop('checked', true);
            checkedRadio.change();
        },
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

            var assessment = new models.Assessment({
                sample_result: model.id     // jshint ignore:line
            });

            if (model.get('assessment')) {
                // We normally would set assessmentModel.id, but, due to
                // a change(https://github.com/jashkenas/backbone/pull/2878) in
                // Backbone, we need to set this on attributes rather than
                // access id directly like we used to. See notes and changes on
                // the pull request for more details.
                assessment.set(assessment.idAttribute, model.get('assessment').id);
            }

            this.variantDetails.show(new this.regionViews.variantDetails({
                result: result
            }));

            this.knowledgeCapture.show(new this.regionViews.knowledgeCapture({
                model: assessment
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
