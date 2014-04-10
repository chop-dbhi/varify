/* global define */

define([
    'cilantro',
    'marionette'
], function(c, Marionette) {

    var AnalysisItem = Marionette.ItemView.extend({
        className: 'analysis-item',

        template: 'varify/analysis/item',

        events: {
            'click': 'onClick'
        },

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
