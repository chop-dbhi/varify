/* global define */

define([
    'underscore',
    'marionette',
    '../../utils',
    'cilantro/utils/numbers'
], function(_, Marionette, utils, Numbers) {

    var Summary = Marionette.ItemView.extend({
        template: 'varify/variant/summary',

        serializeData: function() {
            // Serialize the data normally and then we will update it as needed
            var data = Marionette.ItemView.prototype.serializeData.apply(
                this, arguments);

            // Mark the class to use when displaying the read depth to visually
            // indicate magnitude of read depth.
            data.read_depth_class = utils.depthClass(data.read_depth);  // jshint ignore:line

            data.read_depth_ref = data.read_depth_ref || '--';  // jshint ignore:line
            data.read_depth_alt = data.read_depth_alt || '--';  // jshint ignore:line

            if (data.raw_read_depth) {  // jshint ignore:line
                data.raw_read_depth_class = utils.depthClass(data.raw_read_depth);  // jshint ignore:line
                data.raw_read_depth = '' + data.raw_read_depth + 'x';   // jshint ignore:line
            }
            else {
                data.raw_read_depth = 'n/a';    // jshint ignore:line
                data.raw_read_depth_class = 'muted';    // jshint ignore:line
            }

            if (data.quality) {
                data.quality_class = utils.qualityClass(data.quality);  // jshint ignore:line
            }
            else {
                data.quality = 'n/a';
            }

            data.genotype_value = data.genotype_value || 'n/a'; // jshint ignore:line

            var bases = [];
            for (var key in data.base_counts || {}) {   // jshint ignore:line
                bases.push('' + key + '=' + data.base_counts[key]); // jshint ignore:line
            }

            if (bases.length) {
                data.base_counts = bases.sort().join(', '); // jshint ignore:line
            }
            else {
                data.base_counts = 'n/a';   // jshint ignore:line
            }

            data.pchr = Numbers.toDelimitedNumber(data.variant.pos);

            // TODO: Gene link list could probably be its own collection view
            var name, gene, genes = [];
            for (var i = 0; i < data.variant.uniqueGenes.length; i++) {
                gene = data.variant.uniqueGenes[i];
                name = gene.name || '';

                if (gene.hgnc_id) { // jshint ignore:line
                    genes.push('<a title="' + name + '" target=_blank href=' +
                               '"http://www.genenames.org/data/hgnc_data.php?hgnc_id=' +
                               gene.hgnc_id + '">' + gene.symbol + '</a>');    // jshint ignore:line
                }
                else {
                    genes.push('<span title="' + name + '">' + gene.symbol + '</span>');
                }
            }
            data.genes = genes.join(', ');

            var hgmd = _.pluck(
                _.where(data.variant.phenotypes, function(phenotype) {
                    return phenotype.hgmd_id !== null;  // jshint ignore:line
                }), 'hgmd_id');

            if (hgmd.length) {
                data.hgmd = hgmd.join(', ');
            }
            else {
                data.hgmd = 'n/a';
            }

            return data;
        }
    });

    return {
        Summary: Summary
    };

});
