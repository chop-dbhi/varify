/* global define */

define([
    'cilantro'
], function(c) {

    var ExporterDialog = c.ui.ExporterDialog.extend({
        template: 'varify/export/dialog'
    });

    return {
        ExporterDialog: ExporterDialog
    };

});
