/* global define */

define([
    'underscore',
    'cilantro',
    'backbone',
    'marionette'
], function(_, c, Backbone, Marionette) {

    var EmptyPhenotypeView = c.ui.EmptyView.extend({
        className: 'muted',

        icon: '',

        align: 'left'
    });

    var EmptyVariantView = EmptyPhenotypeView.extend({
        message: 'No associated variant phenotypes'
    });

    var EmptyGeneView = EmptyPhenotypeView.extend({
        message: 'No phenotypes for this gene'
    });

    var PhenotypeItem = Marionette.ItemView.extend({
        template: 'varify/variant/phenotype-item',

        tagName: 'li',

        serializeData: function() {
            var data = Marionette.ItemView.prototype.serializeData.apply(
                this, arguments);

            if (data.hpo_id) {  // jshint ignore:line
                /* jshint ignore:start */
                /*
                 * Zero-pad the HPO ID to force it to be 7 digits. This trick
                 * is from:
                 *
                 *      http://dev.enekoalonso.com/2010/07/20/little-tricks-string-padding-in-javascript/
                 */
                /* jshint ignore:end */
                data.hpo_id = String('0000000' + data.hpo_id).slice(-7);    // jshint ignore:line
            }

            return data;
        }
    });

    var PhenotypeGroup = Marionette.CompositeView.extend({
        template: 'varify/variant/phenotype-group',

        tagName: 'ul',

        className: 'unstyled',

        itemView: PhenotypeItem,

        itemViewContainer: '[data-target=items]',

        getEmptyView: function() {
            if (this.model.get('type') === 'variant') {
                return EmptyVariantView;
            }
            else {
                return EmptyGeneView;
            }
        }
    });

    var Phenotypes = Marionette.CompositeView.extend({
        template: 'varify/variant/phenotypes',

        itemView: PhenotypeGroup,

        itemViewContainer: '[data-target=items]',

        itemViewOptions: function(model) {
            return {
                collection: new Backbone.Collection(
                    _.sortBy(model.get('phenotypes'), function(p) {
                        return p.term;
                    })
                )
            };
        }
    });

    return {
        Phenotypes: Phenotypes
    };

});
