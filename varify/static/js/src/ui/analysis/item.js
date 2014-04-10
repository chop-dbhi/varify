/* global define */

define([
    'marionette',
    'cilantro'
], function(Marionette) {

    var AnalysisItem = Marionette.ItemView.extend({
        className: 'row-fluid analysis-item',

        template: 'varify/analysis/item',

        modelEvents: {
            sync: 'render'
        },

        ui: {
            status: '[data-target=status-label]'
        },

        setStatus: function(cls) {
            this.ui.status.removeClass(
                'label-info label-warning label-success label-important')
                .addClass(cls);
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

    var AssessmentItem = Marionette.ItemView.extend({
        className: 'assessment-item',

        template: 'varify/analysis/assessment-item',

        modelEvents: {
            sync: 'render'
        }
    });

    return {
        AnalysisItem: AnalysisItem,
        AssessmentItem: AssessmentItem
    };

});
