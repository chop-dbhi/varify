/* global define */

define([
    'jquery',
    'underscore',
    'backbone',
    'marionette',
    '../../models',
    '../../utils'
], function($, _, Backbone, Marionette, models, utils) {

    var UserPopoverItem = Marionette.ItemView.extend({
        tagName: 'li',

        template: 'varify/variant/assessment-metrics/user-popover-item'
    });

    var UserPopoverCollection = Marionette.CollectionView.extend({
        className: 'unstyled',

        tagName: 'ul',

        itemView: UserPopoverItem
    });

    var PercentageItem = Marionette.ItemView.extend({
        tagName: 'li',

        template: 'varify/variant/assessment-metrics/percentage-item',

        ui: {
            popover: '[data-target=user-popover]'
        },

        onRender: function() {
            var popoverView = new UserPopoverCollection({
                collection: new Backbone.Collection(this.model.get('users'))
            });

            this.ui.popover.attr(
                'data-content', popoverView.render().el.outerHTML);
        }
    });

    var Percentages = Marionette.CompositeView.extend({
        template: 'varify/variant/assessment-metrics/percentages',

        itemView: PercentageItem,

        itemViewContainer: '[data-target=items]',

        ui: {
            popover: '[data-target=user-popover]',
        },

        initialize: function() {
            _.bindAll(this, 'hidePopover');
        },

        templateHelpers: function() {
            return {
                title: this.options.title
            };
        },

        hidePopover: function(event) {
            // Since we have embedded tags in the popover link, we need to
            // exclude clicks not only on this element but also when the parent
            // of the clicked element is the popover link.
            this.ui.popover.not(event.target)
                .not(event.target.parentElement)
                .popover('hide');
        },

        onClose: function() {
            // Clean up after ourselves. If we don't remove the event handler
            // then we will still receive click notifications even long after
            // we are dead and gone and the hidePopover method will throw a
            // fit because ui.popover is no longer bound.
            $(document).off('click', this.hidePopover);
        },

        onRender: function() {
            $(document).on('click', this.hidePopover);

            this.bindUIElements();

            this.ui.popover.popover({
                container: '#result-details-modal',
                html: true,
                title: 'Users who made this call'
            });
        }
    });

    var AssessmentRow = Marionette.ItemView.extend({
        tagName: 'tr',

        template: 'varify/variant/assessment-metrics/row',

        ui: {
            popover: '[data-target=details-popover]'
        },

        templateHelpers: function() {
            var samplePath = 'samples/' + this.model.get('sample').id;

            return {
                sampleUrl: utils.toAbsolutePath(samplePath)
            };
        },

        onRender: function() {
            this.ui.popover.attr('data-content', '<p class=details-popover-content>' +
                this.model.get('details') + '</p>');
        }
    });

    var AssessmentTable = Marionette.CompositeView.extend({
        template: 'varify/variant/assessment-metrics/table',

        itemView: AssessmentRow,

        itemViewContainer: '[data-target=items]',

        ui: {
            popover: '[data-target=details-popover]',
        },

        initialize: function() {
            _.bindAll(this, 'hidePopover');
        },

        hidePopover: function(event) {
            // Since we have embedded tags in the popover link, we need to
            // exclude clicks not only on this element but also when the parent
            // of the clicked element is the popover link.
            this.ui.popover.not(event.target)
                .not(event.target.parentElement)
                .popover('hide');
        },

        onClose: function() {
            // Clean up after ourselves. If we don't remove the event handler
            // then we will still receive click notifications even long after
            // we are dead and gone and the hidePopover method will throw a
            // fit because ui.popover is no longer bound.
            $(document).off('click', this.hidePopover);
        },

        onRender: function() {
            $(document).on('click', this.hidePopover);

            this.bindUIElements();

            this.ui.popover.popover({
                container: '#result-details-modal',
                placement: 'top',
                html: true,
                title: 'Evidence Details'
            });
        }
    });

    var AssessmentMetrics = Marionette.Layout.extend({
        template: 'varify/variant/assessment-metrics',

        ui: {
            empty: '[data-target=empty-message]',
            error: '[data-target=error-message]',
            loading: '[data-target=loading-indicator]',
            metrics: '[data-target=metrics-container]'
        },

        regions: {
            categories: '[data-target=categories]',
            pathogenicities: '[data-target=pathogenicities]',
            table: '[data-target=assessment-table]'
        },

        modelEvents: {
            'error': 'onError',
            'request': 'onRequest',
            'sync': 'onSync'
        },

        initialize: function() {
            _.bindAll(this, 'onError', 'onRequest', 'onSync');

            if (!this.options.variantId) {
                throw new Error('Variant ID Required');
            }

            this.model = new models.AssessmentMetrics(null, {
                variantId: this.options.variantId
            });
        },

        onError: function() {
            this.ui.empty.hide();
            this.ui.error.show();
            this.ui.loading.hide();
            this.ui.metrics.hide();
        },

        onRequest: function() {
            this.ui.empty.hide();
            this.ui.error.hide();
            this.ui.loading.show();
            this.ui.metrics.hide();
        },

        onSync: function() {
            this.ui.empty.hide();
            this.ui.error.hide();
            this.ui.loading.hide();
            this.ui.metrics.hide();

            if (this.model.get('num_assessments')) {
                this.categories.show(new Percentages({
                    collection: new Backbone.Collection(
                        this.model.get('categories')
                    ),
                    title: 'Categories'
                }));

                this.pathogenicities.show(new Percentages({
                    collection: new Backbone.Collection(
                        this.model.get('pathogenicities')
                    ),
                    title: 'Pathogenicities'
                }));

                this.table.show(new AssessmentTable({
                    collection: new Backbone.Collection(
                        this.model.get('assessments')
                    )
                }));

                this.ui.metrics.show();
            }
            else {
                this.ui.empty.show();
            }
        },

        onRender: function() {
            this.model.fetch();
        }
    });

    return {
        AssessmentMetrics: AssessmentMetrics
    };

});
