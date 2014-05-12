/* global define */

define([
    'underscore',
    'marionette',
    './body',
    './header'
], function(_, Marionette, body, header) {

    // Renders a table with one or more tbody elements each representing a
    // frame of data in the collection.
    var ResultTable = Marionette.CollectionView.extend({
        tagName: 'table',

        className: 'table table-striped',

        collectionEvents: {
            'change:currentpage': 'showCurrentPage'
        },

        itemView: body.ResultBody,

        itemViewOptions: function(item) {
            return _.defaults({collection: item.series}, this.options);
        },

        initialize: function() {
            this.data = {};

            if (!(this.data.view = this.options.view)) {
                throw new Error('view model required');
            }

            this.header = new header.Header({
                view: this.data.view
            });

            this.$el.append(this.header.render().el);

            var _this = this;
            this.collection.on('reset', function() {
                if (_this.collection.objectCount === 0) {
                    _this.$el.hide();
                }
                else {
                    _this.header.render();
                    _this.$el.show();
                }
            });
        },

        showCurrentPage: function(model, num) {
            this.children.each(function(view) {
                view.$el.toggle(view.model.id === num);
            });
        }
    });

    return {
        ResultTable: ResultTable
    };
});
