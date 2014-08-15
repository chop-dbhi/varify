/* global define */

define([
    'jquery',
    'underscore',
    './utils',
    'cilantro/utils/numbers'
], function($, _, utils, Numbers) {

    // Renders a genomic position hyperlink based on chr and pos.
    var genomicPosition = function(chr, pos) {
        var pchr = Numbers.toDelimitedNumber(pos);
        return '<td class=genomic-position><a target=_blank href=' +
               '"http://genome.ucsc.edu/cgi-bin/hgTracks?position=chr' + chr +
               '%3A' + pos + '">chr' + chr + ' <span class=muted>@</span> ' +
               pchr + '</a></td>';
    };

    var phenotypeScore = function(resultScore) {
        if (resultScore) {
            var rank = parseInt(resultScore.rank, 10);
            var score = parseFloat(resultScore.score);

            if (!isNaN(rank) && !isNaN(score)) {
                return '<td>' + rank + ' <small class=muted>(' +
                       (Numbers.prettyNumber(score)) + ')</small></td>';
            }
        }

        return '<td><small class=muted>unranked</small></td>';
    };

    var _renderGene = function(gene) {
        var name = gene.name || '';

        if (gene.hgnc_id) {     // jshint ignore:line
            return '<a title="' + name + '" target=_blank href=' +
                   '"http://www.genenames.org/data/hgnc_data.php?hgnc_id=' +
                   gene.hgnc_id + '">' + gene.symbol + '</a>';  // jshint ignore:line
        }

        return '<span title="' + name + '">' + gene.symbol + '</span>';
    };

    var category = function(assessment) {
        if ((assessment !== null) && (assessment.assessment_category)) {   // jshint ignore:line
            var html = [];
            html.push('<br />Category:');
            html.push(assessment.assessment_category.name);     // jshint ignore:line

            if (assessment.assessment_category.id > 2) {    // jshint ignore:line
                html.push('<span class=muted>(Incidental Finding)</span>');
            }

            return '<span class=assessment-category>' + (html.join(' ')) + '</span>';
        }

        return '';
    };

    var pathogenicity = function(assessment) {
        if ((assessment !== null) && (assessment.pathogenicity)) {
            var html = [];
            html.push('<br />Pathogenicity: ');
            html.push(assessment.pathogenicity.name);
            return '<span class=pathogenicity>' + (html.join('')) + '</span>';
        }

        return '';
    };

    // Takes an array of gene objects with `symbol`, `hgnc_id` and `name` and
    // renders a list of gene names hyperlinks.
    var geneLinks = function(genes, collapse) {
        if (collapse === null) {
            collapse = false;
        }

        var html = [];
        var len = genes.length;

        if (!len) {
            html.push('<span class=muted>Unknown</span>');
        }
        else if (collapse || len === 1) {
            html.push(_renderGene(genes[0]));
        }
        else {
            var results = [];

            for (var i = 0; i < genes.length; i++) {
                results.push(_renderGene(genes[i]));
            }

            html.push(results.join(', '));
        }

        return '<td>' + (html.join(' ')) + '</td>';
    };

    var hgvsC = function(eff) {
        if (eff !== null) {
            var text = eff.hgvs_c || '';    // jshint ignore:line
            return '<td title="' + text + '">' + text + '</td>';
        }

        return '<td></td>';
    };

    var genotype = function(value, description) {
        var title = '' + value + ' (' + description + ')';
        return '<td title="' + title + '">' + value + ' <small>(' +
               description + ')</small></td>';
    };

    var hgvsP = function(eff) {
        if (eff !== null) {
            return '<td>' + (eff.hgvs_p || eff.amino_acid_change || '') + '</td>';  // jshint ignore:line
        }

        return '<td></td>';
    };

    var _renderVariantEffect = function(eff) {
        var html = [];
        html.push('' + eff.type);

        if (eff.transcript !== null) {
            html.push('<small>');
            html.push(eff.transcript.transcript);

            if (eff.segment !== null) {
                html.push(' @ ' + eff.segment);
            }

            html.push('</small>');
        }

        html.push('</small>');
        return html.join(' ');
    };

    var variantEffects = function(effects, collapse) {
        if (collapse === null) {
            collapse = false;
        }

        var html = [];
        var len = effects.length;

        if (!len) {
            return '<span class=muted>No Effects</span>';
        }
        else if (collapse || len === 1) {
            var labelClass = utils.priorityClass(
                utils.effectImpactPriority(effects[0].impact));
            html.push('<span class="' + labelClass + '">' +
                      (_renderVariantEffect(effects[0])) + '</span>');
        }
        else {
            var results = [];

            for (var i = 0; i < effects.length; i++) {
                results.push(_renderVariantEffect(effects[i]));
            }

            html.push(results.join(', '));
        }

        return '<td>' + (html.join(' ')) + '</td>';
    };

    var condensedFlags = function(attrs) {
        var flags = [];
        flags.push(['dbSNP', attrs.rsid !== null]);
        flags.push(['HGMD', _.pluck(attrs.phenotypes, 'hgmd_id').length > 0]);
        flags.push(['1000g', attrs['1000g'].length > 0]);
        flags.push(['EVS', attrs.evs.length > 0]);

        if (attrs.solvebio && attrs.solvebio.clinvar) {
            flags.push(['ClinVar', attrs.solvebio.clinvar.total > 0]);
        }

        var html = [], label, present, klass;
        for (var i = 0; i < flags.length; i++) {
            label = flags[i][0];
            present = flags[i][1];

            klass = present ? 'text-info' : 'muted';

            html.push('<span class="flag ' + klass + '">' + label + '</span>');
        }

        return '<td class=flags-container><span class=flags>' +
               (html.join('')) + '<span></td>';
    };

    var dbSNPLink = function(rsid) {
        return '<a target=_blank href=' +
               '"http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=' +
               rsid + '">' + rsid + '</a>';
    };

    return {
        category: category,
        condensedFlags: condensedFlags,
        dbSNPLink: dbSNPLink,
        hgvsC: hgvsC,
        hgvsP: hgvsP,
        geneLinks: geneLinks,
        genomicPosition: genomicPosition,
        genotype: genotype,
        pathogenicity: pathogenicity,
        phenotypeScore: phenotypeScore,
        variantEffects: variantEffects
    };
});
