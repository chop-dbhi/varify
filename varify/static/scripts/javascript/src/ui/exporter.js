/* global define */

define([
    'cilantro'
], function(c) {

    var ExporterDialog = c.ui.ExporterDialog.extend({
        template: 'varify/export/dialog',

        _events: {
            'click [data-action=change-columns]': 'changeColumnsClicked'
        },

        initialize: function() {
            this.events = _.extend({}, this._events, this.events);

            c.ui.ExporterDialog.prototype.initialize.call(this);
        },

        changeColumnsClicked: function() {
            c.dialogs.columns.open();
        }
    });

    return {
        ExporterDialog: ExporterDialog
    };

});
