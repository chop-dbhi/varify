/* global define */

define([
    'underscore',
    'marionette'
], function(_, Marionette) {

    var AnnotationEmptyView = Marionette.ItemView.extend({
        tagName: 'span',

        className: 'muted',

        template: 'varify/modals/phenotype/empty',

        serializeData: function() {
            return {'name': this.options.name};
        }
    });

    var AnnotationItem = Marionette.ItemView.extend({
        tagName: 'li',

        template: 'varify/modals/phenotype/annotationsItem'
    });

    var Annotations = Marionette.CompositeView.extend({
        template: 'varify/modals/phenotype/annotations',

        itemView: AnnotationItem,

        emptyView: AnnotationEmptyView,

        itemViewContainer: '[data-target=annotation-list]',

        itemViewOptions: function() {
            return {'name': this.options.name};
        }
    });

    return {
        Annotations: Annotations
    };

});
