/* global define */

define([
    'jquery',
    'marionette',
    'cilantro',
    '../../models',
    '../../templates'
], function($, Marionette, c, models, Templates) {

    var ResultRow = Marionette.ItemView.extend({
        className: 'area-container variant-container',

        template: function() {},

        tagName: 'tr',

        events: {
            'click': 'onClick'
        },

        onClick: function() {
            c.dialogs.resultDetails.open(this.model);
        },

        onRender: function() {
            var $condensedFlags, $gene, $genomicPosition, $genotype, $hgvsC,
                $hgvsP, $phenotypeScore, $variantEffects, assessment, resultScore,
                variant;

            variant = this.model.get('variant');
            resultScore = this.model.get('score');
            assessment = this.model.get('assessment');

            $gene = $(Templates.geneLinks(variant.uniqueGenes, {
                collapse: true
            })).addClass('genes');

            $hgvsP = $(Templates.hgvsP(variant.effects[0])).addClass('hgvs-p');

            $variantEffects = $(Templates.variantEffects(variant.effects, true))
                .addClass('variant-effects')
                .append($(Templates.pathogenicity(assessment)));

            /*
             * NOTE: As of Bootstrap 2.3.1 there is still an issue with adding
             * tooltips to <td> elements directly as the tooltip will be
             * instered directly into the table, causing the row to be
             * misaligned. The workaround(added in 2.3.0) is to set the
             * container to body so that the div is not jammed into the table
             * all willy-nilly like.
             */
            $hgvsC = $(Templates.hgvsC(variant.effects[0])).addClass('hgvs-c').tooltip({
                container: 'body'
            });

            $genotype = $(Templates.genotype(
                    this.model.get('genotype_value'),
                    this.model.get('genotype_description'))
                ).addClass('genotype').tooltip({container: 'body'});

            $genomicPosition = $(Templates.genomicPosition(variant.chr, variant.pos))
                .addClass('genomic-position')
                .append($(Templates.category(assessment)));

            $phenotypeScore = $(Templates.phenotypeScore(resultScore))
                .addClass('phenotype-score');

            $condensedFlags = $(Templates.condensedFlags(variant));

            this.$el.empty();
            return this.$el.append($gene, $hgvsP, $variantEffects, $hgvsC,
                                   $genotype, $genomicPosition, $phenotypeScore,
                                   $condensedFlags);
        }
    });

    var EmptyResultRow = c.ui.LoadView.extend({
        align: 'left',

        tagName: 'tr'
    });

    return {
        ResultRow: ResultRow,
        EmptyResultRow: EmptyResultRow
    };
});
