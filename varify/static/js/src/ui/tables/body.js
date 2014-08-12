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
            this._collection = options.collection;
            this.collection = new models.ResultCollection();

            this.listenTo(this._collection, 'reset', this._fetch);

            if (this._collection.length > 0) this._fetch();
        },

        _fetch: function() {
            this.collection.fetch({
                data: JSON.stringify({ids: this._collection.pluck('pk')}),
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
