/* global define */

define([
    'underscore',
    'marionette',
    '../../models',
    './row'
], function(_, Marionette, models, row) {

    // Represents a "frame" of rows. The model is referenced for keeping
    // track which frame this is relative to the whole series.
    var ResultBody = Marionette.CollectionView.extend({
        tagName: 'tbody',

        template: function() {},

        initialize: function(options) {
            this.collection = new models.ResultCollection();
            var data = {ids: options.collection.pluck('pk')};
            this.collection.fetch({
                data: JSON.stringify(data),
                type: 'POST',
                contentType: 'application/json',
                parse: true
            });
        },

        itemView: row.ResultRow
    });

    return {
        ResultBody: ResultBody
    };

});
