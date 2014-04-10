/* global define */

define([
    'underscore',
    'marionette',
    './item'
], function(_, Marionette, item) {

    var AnalysisList = Marionette.CompositeView.extend({
        itemView: item.AnalysisItem,

        itemViewContainer: '.items',

        template: 'varify/analysis/list',

        ui: {
            empty: '.empty-message',
            error: '.error-message',
            loading: '.loading-indicator'
        },

        collectionEvents: {
            sync: 'onCollectionSync',
            error: 'onCollectionError',
            request: 'onCollectionRequest'
        },

        onCollectionError: function() {
            this.ui.empty.hide();
            this.ui.error.show();
            this.ui.loading.hide();
        },

        onCollectionRequest: function() {
            this.ui.empty.hide();
            this.ui.error.hide();
            this.ui.loading.show();
        },

        onCollectionSync: function() {
            this.ui.error.hide();
            this.ui.loading.hide();
            this.checkForEmptyCollection();
        },

        initialize: function() {
            _.bindAll(this, 'onCollectionError', 'onCollectionRequest',
                      'onCollectionSync');

            this.collection.fetch();
        },

        checkForEmptyCollection: function() {
            if (this.collection.length === 0) {
                this.ui.empty.show();
            }
            else {
                this.ui.empty.hide();
            }
        },

        onRender: function() {
            this.checkForEmptyCollection();
        }
    });

    var AssessmentList = Marionette.CompositeView.extend({
        itemView: item.AssessmentItem,

        itemViewContainer: '.items',

        template: 'varify/analysis/assessment-list',

        ui: {
            empty: '.empty-message',
            error: '.error-message',
            initial: '.initial-message',
            loading: '.loading-indicator'
        },

        collectionEvents: {
            sync: 'onCollectionSync',
            error: 'onCollectionError',
            request: 'onCollectionRequest'
        },

        onCollectionError: function() {
            this.ui.empty.hide();
            this.ui.error.show();
            this.ui.initial.hide();
            this.ui.loading.hide();
        },

        onCollectionRequest: function() {
            this.ui.empty.hide();
            this.ui.error.hide();
            this.ui.initial.hide();
            this.ui.loading.show();
        },

        onCollectionSync: function() {
            this.ui.error.hide();
            this.ui.loading.hide();
            this.checkForEmptyCollection();
        },

        initialize: function() {
            _.bindAll(this, 'onCollectionError', 'onCollectionRequest',
                      'onCollectionSync');
        },

        checkForEmptyCollection: function() {
            if (this.collection.length === 0) {
                this.ui.empty.show();
            }
            else {
                this.ui.empty.hide();
            }
        },
    });

    return {
        AnalysisList: AnalysisList,
        AssessmentList: AssessmentList
    };

});
