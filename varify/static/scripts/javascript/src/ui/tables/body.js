/* global define */

define([
    'underscore',
    'marionette',
    './row'
], function(_, Marionette, row) {

    // Represents a "frame" of rows. The model is referenced for keeping
    // track which frame this is relative to the whole series.
    var ResultBody = Marionette.CollectionView.extend({
        tagName: 'tbody',

        template: function() {},

        itemView: row.ResultRow,

        itemViewOptions: function (model, index) {
            return _.defaults({resultPk: model.get('pk')}, this.options);
        }
    });

    return {
        ResultBody: ResultBody
    };

});
