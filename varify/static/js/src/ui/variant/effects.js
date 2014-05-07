/* global define */

define([
    'underscore',
    'cilantro',
    'backbone',
    'marionette',
    '../../utils'
], function(_, c, Backbone, Marionette, utils) {

    var EffectItem = Marionette.ItemView.extend({
        tagName: 'li',

        template: 'varify/variant/effect-item',

        templateHelpers: function() {
            var hgvsc = this.model.get('hgvs_c') || '',
                segment = this.model.get('segment') || '',
                hgvscOrSegment = '';

            if (hgvsc) {
                hgvscOrSegment = hgvsc + ' ' + segment;
            }
            else {
                hgvscOrSegment = segment;
            }

            var gene, transcript = this.model.get('transcript'),
                uniqueGenes = this.model.get('uniqueGenes');

            if (uniqueGenes && uniqueGenes.length && transcript) {
                gene = transcript.gene;
            }

            var proteinChange,
                changeString = this.model.get('hgvs_p') ||
                    this.model.get('amino_acid_change');

            if (changeString) {
                /*
                 *  Key is the basic physicochemical property of the amino acid
                 *  And each character in the value string are the categorizations
                 *  Inspecting the hgvs_p will tell us about the protein change
                 *  For more info refer to
                 *  https://www.ncbi.nlm.nih.gov/Class/Structure/aa/aa_explorer.cgi
                 */

                var changes = {
                    'Non-Polar': 'IFVLWMAGP',
                    'Polar': 'CYTSNQ',
                    'Negative': 'ED',
                    'Positive': 'HKR'
                };
                var initialAminoAcid = changeString[2],
                    finalAminoAcid = changeString[changeString.length - 1],
                    initialProperty = '',
                    finalProperty = '';

                // Check if there was a change in the hgvs_p
                for (var change in changes) {
                    if (changes[change].indexOf(initialAminoAcid) !== -1) {
                        initialProperty = change;
                    }
                    if (changes[change].indexOf(finalAminoAcid) !== -1) {
                        finalProperty = '&#8594' + change;
                    }
                }

                if (initialProperty && finalProperty) {
                    proteinChange = initialProperty + finalProperty;
                }
            }

            return {
                hgvscOrSegment: hgvscOrSegment,
                gene: gene,
                changeString: changeString,
                proteinChange: proteinChange
            };
        }
    });

    var EffectType = Marionette.CompositeView.extend({
        tagName: 'ul',

        className: 'unstyled',

        template: 'varify/variant/effect-type',

        itemViewContainer: '[data-target=items]',

        itemView: EffectItem,

        templateHelpers: function() {
            var priorityClass = '';

            if (this.collection.length) {
                priorityClass = utils.priorityClass(
                    utils.effectImpactPriority(
                        this.collection.models[0].get('impact')));
            }

            return {
                priorityClass: priorityClass
            };
        }
    });

    var NoEffectsView = c.ui.EmptyView.extend({
        className: 'muted',

        icon: '',

        message: 'No SNPEff effects known',

        align: 'left'
    });

    var Effects = Marionette.CompositeView.extend({
        template: 'varify/variant/effects',

        emptyView: NoEffectsView,

        itemViewContainer: '[data-target=items]',

        itemView: EffectType,

        itemViewOptions: function(model) {
            return {
                collection: new Backbone.Collection(model.get('effects'))
            };
        }
    });

    return {
        Effects: Effects
    };

});
