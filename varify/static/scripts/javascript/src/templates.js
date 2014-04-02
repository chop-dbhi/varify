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
        return '<td class=genomic-position><a target=_blank href="http://genome.ucsc.edu/cgi-bin/hgTracks?position=chr' + chr + '%3A' + pos + '">chr' + chr + ' <span class=muted>@</span> ' + pchr + '</a></td>';
    };

    var phenotypeScore = function(resultScore) {
        if (resultScore != null) {
            var rank = parseInt(resultScore.rank, 10);
            var score = parseFloat(resultScore.score);

            if (!isNaN(rank) && !isNaN(score)) {
                return '<td>' + rank + ' <small class=muted>(' + (Numbers.prettyNumber(score)) + ')</small></td>';
            }
        }

        return '<td><small class=muted>unranked</small></td>';
    };

    var _renderGene = function(gene) {
        var name = gene.name || '';

        if (gene.hgnc_id) {
            return '<a title="' + name + '" target=_blank href="http://www.genenames.org/data/hgnc_data.php?hgnc_id=' + gene.hgnc_id + '">' + gene.symbol + '</a>';
        }

        return '<span title="' + name + '">' + gene.symbol + '</span>';
    };

    var category = function(assessment) {
        if ((assessment != null) && (assessment.assessment_category != null)) {
            var html = [];
            html.push('<br />Category:');
            html.push(assessment.assessment_category.name);

            if (assessment.assessment_category.id > 2) {
                html.push('<span class=muted>(Incidental Finding)</span>');
            }

            return '<span class=assessment-category>' + (html.join(' ')) + '</span>';
        }

        return '';
    };

    var pathogenicity = function(assessment) {
        if ((assessment != null) && (assessment.pathogenicity != null)) {
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
        if (collapse == null) {
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
        if (eff != null) {
            text = eff.hgvs_c || '';
            return '<td title="' + text + '">' + text + '</td>';
        }

        return '<td></td>';
    };

    var genotype = function(value, description) {
        var title = '' + value + ' (' + description + ')';
        return '<td title="' + title + '">' + value + ' <small>(' + description + ')</small></td>';
    };

    var hgvsP = function(eff) {
        if (eff != null) {
            return '<td>' + (eff.hgvs_p || eff.amino_acid_change || '') + '</td>';
        }

        return '<td></td>';
    };

    var _renderVariantEffect = function(eff) {
        var html = [];
        html.push('' + eff.type);

        if (eff.transcript != null) {
            html.push('<small>');
            html.push(eff.transcript.transcript);

            if (eff.segment != null) {
                html.push(' @ ' + eff.segment);
            }

            html.push('</small>');
        }

        html.push('</small>');
        return html.join(' ');
    };

    var variantEffects = function(effects, collapse) {
        if (collapse == null) {
            collapse = false;
        }

        var html = [];
        var len = effects.length;

        if (!len) {
            return '<span class=muted>No Effects</span>';
        }
        else if (collapse || len === 1) {
            var labelClass = utils.priorityClass(utils.effectImpactPriority(effects[0].impact));
            html.push('<span class="' + labelClass + '">' + (_renderVariantEffect(effects[0])) + '</span>');
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
        flags.push(['dbSNP', attrs['rsid'] != null]);
        flags.push(['HGMD', _.pluck(attrs['phenotypes'], 'hgmd_id').length > 0]);
        flags.push(['1000g', attrs['1000g'].length > 0]);
        flags.push(['EVS', attrs['evs'].length > 0]);

        if (!! attrs['solvebio']) {
            flags.push(['ClinVar', attrs['solvebio']['clinvar'].length > 0]);
        }

        var html = [], label, present, klass;
        for (var i = 0; i < flags.length; i++) {
            label = flags[i][0];
            present = flags[i][1];

            klass = present ? 'text-info' : 'muted';

            html.push('<span class="flag ' + klass + '">' + label + '</span>');
        }

        return '<td class=flags-container><span class=flags>' + (html.join('')) + '<span></td>';
    };

    var cohortVariantDetailList = function(cohorts) {
        var html = [], cohort, cohortHtml, sample, sampleNames, sortedSamples, samplePath, popoverHtml;

        for (var i = 0; i < cohorts.length; i++) {
            cohort = cohorts[i]
            cohortHtml = '<small>' + cohort.name + '</small> ' + (Numbers.prettyNumber(cohort.af * 100)) + '% <span class=muted>(' + cohort.size + ')</span>';

            sampleNames = [];
            sortedSamples = _.sortBy(cohort.samples, function(s) {
                return s.name;
            });

            for (var j = 0; j < sortedSamples.length; j++) {
                sample = sortedSamples[j];
                samplePath = '/workspace/samples/' + sample.id;
                sampleNames.push('<a href="' + (utils.toAbsolutePath(samplePath)) + '/">' + sample.name + '</a>');
            }

            sampleHtml = sampleNames.join('<br />');
            popoverHtml = '<div>' + ($('<div />').html(sampleHtml).html()) + '</div>';
            html.push('<li class=cohort-details><a href="#" class=cohort-sample-popover data-content=\'' + popoverHtml + '\'>' + cohortHtml + '</a></li>');
        }

        return '<ul class=unstyled>' + (html.join('')) + '</ul>';
    };

    var dbSNPLink = function(rsid) {
        return '<a target=_blank href="http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=' + rsid + '">' + rsid + '</a>';
    };

    var assessmentMetrics = function(items, usernamePopover) {
        if (usernamePopover == null) {
            usernamePopover = false;
        }

        var html = [];
        _.each(items, function(item, key) {
            var popoverHtml,  username, usernames;

            var callIndicator = item.is_user_call ? '*' : '';
            var name = (key != null) && key !== '' ? key : 'N/A';
            var prefixHtml = '<small>' + name + '</small>  ' + (Numbers.prettyNumber(item.percentage)) + '% ';
            var countHtml = '<span class=muted>(' + item.count + ')' + callIndicator + '</span>';

            if (item.usernames.length > 0 && usernamePopover) {
                usernames = [];

                for (var i = 0; i < items.usernames; i++) {
                    usernames.push(items.usernames[i]);
                }

                popoverHtml = usernames.join('<br />');
                countHtml = '<a href="#" class=username-popover data-trigger=hover title="Users who made this call" data-html=true data-placement=top data-content="' + popoverHtml + '">' + countHtml + '</a>';
            }

            html.push('<li>' + prefixHtml + countHtml + '</li>');
        });

        return '<ul class=unstyled>' + (html.join('')) + '</ul>';
    };

    var assessmentRows = function(assessments) {
        var html = [];
        var groupedAssessments = _.chain(assessments).groupBy('pathogenicity').value();

        _.each(groupedAssessments, function(assessmentList, pathogenicity) {
            var assessment, assessmentHasDetails, samplePath;

            for (var i = 0; i < assessmentList.length; i++) {
                assessment = assessmentList[i];
                assessmentHasDetails = assessment.details != null;

                html.push('<tr id=assessment-row-' + assessment.id + '>');

                if (assessmentHasDetails) {
                    html.push('<td><a href=#><i class=icon-plus></i><i class="icon-minus hide"></i></a></td>');
                }
                else {
                    html.push('<td></td>');
                }

                samplePath = '/workspace/samples/' + assessment.sample.id;
                html.push('<td><a href="' + (utils.toAbsolutePath(samplePath)) + '/">' + assessment.sample.name + '</a></td>');

                if (!_.isEmpty(assessment.user.email)) {
                    html.push('<td><a href="mailto:' + assessment.user.email + '">' + assessment.user.username + '</a></td>');
                }
                else {
                    html.push('<td>' + assessment.user.username + '</td>');
                }

                html.push('<td>' + assessment.pathogenicity + '</td>');
                html.push('<td>' + assessment.category + '</td>');
                html.push('<td>' + assessment.mother_result + '</td>');
                html.push('<td>' + assessment.father_result + '</td>');
                html.push('<td>' + assessment.sanger + '</td>');

                html.push('</tr>');

                if (assessmentHasDetails) {
                    html.push('<tr class="hide no-border" id=assessment-row-' + assessment.id + '-details><td></td><td colspan=7><strong>Evidence Details: </strong>' + assessment.details + '</td></tr>');
                }
            }
        });

        return html.join('');
    };

    var hgmdLinks = function(phenotypes) {
        var hgmdPhenotypes = [];

        for (var i = 0; i < phenotypes.length; i++) {
            if (phenotypes[i].hgmd_id != null) {
                hgmdPhenotypes.push(phenotypes[i].hgmd_id);
            }
        }

        return hgmdPhenotypes.join(', ');
    };

    return {
        assessmentMetrics: assessmentMetrics,
        assessmentRows: assessmentRows,
        category: category,
        cohortVariantDetailList: cohortVariantDetailList,
        condensedFlags: condensedFlags,
        dbSNPLink: dbSNPLink,
        hgmdLinks: hgmdLinks,
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
