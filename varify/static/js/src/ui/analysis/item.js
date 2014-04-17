/* global define */

define([
    'underscore',
    'cilantro',
    'marionette'
], function(_, c, Marionette) {

    var StatusItem = Marionette.ItemView.extend({
        ui: {
            status: '[data-target=status-label]'
        },

        modelEvents: {
            sync: 'render'
        },

        setStatus: function(cls) {
            this.ui.status.removeClass(
                'label-info label-warning label-success label-important')
                .addClass(cls);
        },
    });

    var AnalysisItem = StatusItem.extend({
        className: 'analysis-item',

        template: 'varify/analysis/item',

        events: {
            'click a': 'onClick'
        },

        onClick: function() {
            c.trigger('analysis:item:click', this, this.model);
        },

        onRender: function() {
            switch(this.model.get('status')) {
                case 'Open':
                    this.setStatus('label-info');
                    break;
                case 'Pending':
                    this.setStatus('label-warning');
                    break;
                case 'Complete':
                    this.setStatus('label-success');
                    break;
                default:
                    this.setStatus('label-important');
                    break;
            }
        }
    });

    var AssessmentItem = StatusItem.extend({
        className: 'assessment-item',

        template: 'varify/analysis/assessment-item',

        ui: function() {
            return _.extend({
                pathogenicity: '.pathogenicity-label',
                category: '.category-label'
            }, StatusItem.prototype.ui);
        },

        onRender: function() {
            switch(this.model.get('status')) {
                case 'Draft':
                    this.setStatus('label-info');
                    break;
                case 'Pending':
                    this.setStatus('label-warning');
                    break;
                case 'Complete':
                    this.setStatus('label-success');
                    break;
                default:
                    this.setStatus('label-important');
                    break;
            }

            if (this.model.get('pathogenicity').name !== this.options.pathogenicity) {
                this.ui.pathogenicity.addClass('text-warning').removeClass('muted');
            }

            if (this.model.get('assessment_category').name !== this.options.category) {
                this.ui.category.addClass('text-warning').removeClass('muted');
            }
        }
    });

    return {
        AnalysisItem: AnalysisItem,
        AssessmentItem: AssessmentItem
    };

});
