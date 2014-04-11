/* global define */

define([
    'underscore',
    'cilantro',
    'backbone',
    'marionette',
    './item',
    '../tables'
], function(_, c, Backbone, Marionette, item, tables) {

    var AnalysisList = Marionette.CompositeView.extend({
        itemView: item.AnalysisItem,

        itemViewContainer: '.items',

        template: 'varify/analysis/list',

        ui: {
            empty: '.empty-message',
            error: '.error-message',
            loading: '.loading-indicator',
            items: '.items'
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
                      'onCollectionSync', 'onAnalysisItemClick');

            c.on('analysis:item:click', this.onAnalysisItemClick);

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
        },

        onAnalysisItemClick: function(view, model) {
            this.ui.items.children().removeClass('selected');
            view.$el.addClass('selected');
        }
    });

    var AssessmentList = Marionette.CompositeView.extend({
        itemView: item.AssessmentItem,

        itemViewContainer: '.items',

        template: 'varify/analysis/assessment-list',

        initialize: function() {
            this.collection = new Backbone.Collection(
                this.model.get('assessments'));
        }
    });

    var ResultList = c.ui.AccordianSection.extend({
        itemView: tables.ResultRow,

        template: 'varify/analysis/result-list',

        itemViewContainer: '.items',

        itemViewOptions: function (model, index) {
            return _.defaults({resultPk: model.get('id')}, this.options);
        },

        initialize: function() {
            this.collection = new Backbone.Collection(
                this.model.get('results'));
        }
    });

    var CategoryList = c.ui.AccordianGroup.extend({
        itemView: ResultList,

        template: 'varify/analysis/category-list',

        itemViewContainer: '.items',

        ui: function() {
            return _.extend({
                totals: '[data-target=totals]'
            }, c.ui.AccordianGroup.prototype.ui);
        },

        initialize: function() {
            c.ui.AccordianGroup.prototype.initialize();

            c.ui.AccordianGroup.prototype.collection = new Backbone.Collection(
                this.model.get('categories'));
        },

        onCompositeCollectionRendered: function() {
            // Since we record the total number of assessments for each
            // item, we can use that as the determining factor of "emptiness."
            if (this.model.get('total_count') > 0) {
                this.ui.heading.css('cursor', 'pointer');
            }
            else {
                this.ui.heading.css('cursor', 'auto');
                this.ui.icon.hide();
                this.ui.totals.hide();
            }
        }
    });

    var PathogenicityList = Marionette.CompositeView.extend({
        itemView: CategoryList,

        itemViewContainer: '.items',

        template: 'varify/analysis/pathogenicity-list',

        ui: {
            empty: '.empty-message',
            error: '.error-message',
            initial: '.initial-message',
            loading: '.loading-indicator',
            items: '.items'
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
            this.ui.items.hide();
            this.ui.loading.show();
        },

        onCollectionSync: function() {
            this.ui.error.hide();
            this.ui.loading.hide();
            this.checkForEmptyCollection();
        },

        initialize: function() {
            _.bindAll(this, 'onCollectionError', 'onCollectionRequest',
                      'onCollectionSync', 'onAnalysisItemClick');

            c.on('analysis:item:click', this.onAnalysisItemClick);
        },

        checkForEmptyCollection: function() {
            if (this.collection.length === 0) {
                this.ui.empty.show();
            }
            else {
                this.ui.items.show();
                this.ui.empty.hide();
            }
        },

        onAnalysisItemClick: function(view, model) {
            // If we are already looking at the assessments for this analysis
            // then don't bother reloading it.
            if (this.model && this.model.id === model.id) return;

            this.model = model;

            this.render();

            this.collection.analysisId = this.model.id;
            this.collection.fetch({reset: true});
        }
    });

    return {
        AnalysisList: AnalysisList,
        PathogenictyList: PathogenicityList
    };

});
