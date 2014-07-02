/* global define */

define([
    'underscore',
    'marionette'
], function(_, Marionette) {

    var DiagnosesEmptyView = Marionette.ItemView.extend({
        tagName: 'span',

        className: 'muted',

        template: 'varify/modals/phenotype/empty',

        serializeData: function() {
            return {'name': this.options.name};
        }
    });

    var DiagnoseItem = Marionette.ItemView.extend({
        tagName:'li',

        template: 'varify/modals/phenotype/diagnosesItem'
    });

    var Diagnoses = Marionette.CompositeView.extend({
        template: 'varify/modals/phenotype/diagnoses',

        itemView: DiagnoseItem,

        emptyView: DiagnosesEmptyView,

        itemViewContainer: '[data-target=items]',

        // Function needed to render different names diagnoses types.
        serializeData: function() {
            return {'name': this.options.name};
        },

        itemViewOptions: function() {
            return {'name': this.options.name};
        }
    });

    return {
        Diagnoses: Diagnoses
    };

});
