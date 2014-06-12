/* global define */

define([
    'underscore',
    'marionette',
    'cilantro',
    '../models',
    '../utils'
], function(_, Marionette, c, models, utils) {

    var SampleView = Marionette.ItemView.extend({
        serializeData: function() {
            if (!this.model) return;

            var data = this.model.toJSON();
            data.loaded = (new Date(data.created)).toLocaleDateString();

            return data;
        }
    });


    var SampleDetail = SampleView.extend({
        template: 'varify/sample/detail'
    });


    var SampleVariantSet = Marionette.ItemView.extend({
        template: 'varify/sample/variant-set',

        serializeData: function() {
            var data = this.model.toJSON();

            data.modified = (new Date(data.modified)).toLocaleString();
            data.created = (new Date(data.created)).toLocaleString();
            data.url = this.model.url();
            data.workflowUrl = utils.toAbsolutePath('variant-sets/' + this.model.id);

            return data;
        }
    });

    var EmptySampleVariantSets = c.ui.EmptyView.extend({
        align: 'left',

        icon: '',

        message: 'No variant sets have been created for this sample.'
    });


    var SampleVariantSets = Marionette.CollectionView.extend({
        itemView: SampleVariantSet,

        emptyView: EmptySampleVariantSets
    });


    var SampleLoader = Marionette.ItemView.extend({
        className: 'sample-loader',

        template: 'varify/sample/loader',

        ui: {
            'loadingMessage': '.loading-message',
            'errorMessage': '.error-message'
        },

        initialize: function() {
            _.bindAll(this, 'onSampleFetchError', 'onSampleFetchSuccess');

            this.data = {};

            if (!(this.data.context = this.options.context)) {
                throw new Error('context model required');
            }

            this.on('router:load', this.onRouterLoad);
        },

        onRouterLoad: function(router, fragment, id) {
            var requestedSampleId = parseInt(id) || null;

            if (requestedSampleId) {
                this.sample = new models.Sample({
                    id: requestedSampleId
                });

                this.sample.fetch({
                    success: this.onSampleFetchSuccess,
                    error: this.onSampleFetchError
                });
            }
            else {
                this.showError('There was an issue parsing the sample ID. ' +
                               'Please make sure it is valid and try again');
            }
        },

        showError: function(text) {
            this.ui.loadingMessage.hide();
            this.ui.errorMessage.text(text).show();
        },

        onSampleFetchError: function() {
            this.showError('There was an error retrieving the sample ' +
                           'details in order to update your filters. Please ' +
                           'make sure that the sample ID is valid and then ' +
                           'try reloading this page.');
        },

        onSampleFetchSuccess: function() {
            // Since this page relies on the user clicking a link on the
            // results page, there must have already been a sample selected. If
            // not, show an error message.
            var json = _.clone(this.data.context.get('json')),
                foundSample = false;

            if (json && json.children && json.children.length) {
                for (var i = 0; i < json.children.length; i++) {
                    if (json.children[i].concept === 2) {
                        json.children[i].value[0].label = this.sample.get('label');
                        json.children[i].value[0].value = this.sample.id;

                        foundSample = true;
                        break;
                    }
                }
            }

            if (foundSample) {
                this.data.context.save('json', json, {reset: true});
                c.router.navigate('results', {trigger: true});
            }
            else {
                this.showError('Could not find sample filter. Make sure ' +
                               'that you currently have a filter selected ' +
                               'in the Proband control on the Query and ' +
                               'that the filter is applied then try again.');
            }
        }
    });


    return {
        SampleView: SampleView,
        SampleDetail: SampleDetail,
        SampleVariantSet: SampleVariantSet,
        SampleVariantSets: SampleVariantSets,
        SampleLoader: SampleLoader
    };

});
