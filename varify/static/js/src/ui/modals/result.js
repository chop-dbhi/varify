/* global define */

define([
    'jquery',
    'underscore',
    'backbone',
    'marionette',
    '../result-details'
], function($, _, Backbone, Marionette, details) {

    var ResultDetailsModal = Marionette.Layout.extend({
        id: 'result-details-modal',

        className: 'modal hide',

        template: 'varify/modals/result',

        events: {
            'click [data-action=close-result-modal]': 'close'
        },

        regions: {
            details: '.variant-details-container'
        },

        close: function() {
            this.$el.modal('hide');
        },

        onRender: function() {
            this.$el.modal({
                show: false,
                keyboard: false,
                backdrop: 'static'
            });
        },

        open: function(result) {
            this.$el.modal('show');

            this.details.show(new details.ResultDetails({
                result: result
            }));
        }

    });

    return {
        ResultDetailsModal: ResultDetailsModal
    };

});
