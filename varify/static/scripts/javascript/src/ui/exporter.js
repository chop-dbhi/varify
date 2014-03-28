/* global define */

define([
    'underscore',
    'cilantro'
], function(_, c) {

    var ExporterDialog = c.ui.ExporterDialog.extend({
        template: 'varify/export/dialog',

        events: function() {
            return _.extend({
                'click [data-action=change-columns]': 'changeColumnsClicked'
            }, c.ui.ExporterDialog.prototype.events);
        },

        changeColumnsClicked: function() {
            c.dialogs.columns.open();
        }
    });

    return {
        ExporterDialog: ExporterDialog
    };

});
