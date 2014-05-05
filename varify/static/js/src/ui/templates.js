/* global define */

define([
    'cilantro',
    'tpl!../../../templates/controls/polyphen.html',
    'tpl!../../../templates/controls/sift.html',
    'tpl!../../../templates/export/dialog.html',
    'tpl!../../../templates/modals/phenotypes.html',
    'tpl!../../../templates/modals/result.html',
    'tpl!../../../templates/modals/sample.html',
    'tpl!../../../templates/sample/loader.html',
    'tpl!../../../templates/sample/row.html',
    'tpl!../../../templates/sample/table.html',
    'tpl!../../../templates/tables/header.html',
    'tpl!../../../templates/variant/article-item.html',
    'tpl!../../../templates/variant/article-group.html',
    'tpl!../../../templates/variant/articles.html',
    'tpl!../../../templates/variant/assessment-metrics.html',
    'tpl!../../../templates/variant/assessment-metrics/percentages.html',
    'tpl!../../../templates/variant/assessment-metrics/percentage-item.html',
    'tpl!../../../templates/variant/assessment-metrics/user-popover-item.html',
    'tpl!../../../templates/variant/cohort-item.html',
    'tpl!../../../templates/variant/cohort-popover-item.html',
    'tpl!../../../templates/variant/cohorts.html',
    'tpl!../../../templates/variant/effect-item.html',
    'tpl!../../../templates/variant/effect-type.html',
    'tpl!../../../templates/variant/effects.html',
    'tpl!../../../templates/variant/frequencies.html',
    'tpl!../../../templates/variant/phenotype-item.html',
    'tpl!../../../templates/variant/phenotype-group.html',
    'tpl!../../../templates/variant/phenotypes.html',
    'tpl!../../../templates/variant/scores.html',
    'tpl!../../../templates/variant/clinvar.html',
    'tpl!../../../templates/variant/clinvar-item.html',
    'tpl!../../../templates/variant/summary.html',
    'tpl!../../../templates/workflows/results.html'
], function(c, polyphen, sift, exportDialog, phenotype, result, sample,
            sampleLoader, sampleRow, sampleTable, header, articleItem,
            articleGroup, variantArticles, assessmentMetrics,
            metricsPercentages, metricsPercentageItem, userPopoverItem,
            cohortItem, cohortPopoverItem, variantCohorts, effectItem,
            effectType, variantEffects, variantFrequencies, phenotypeItem,
            phenotypeGroup, variantPhenotypes, variantScores, clinvar,
            clinvarItem, variantSummary, results) {

    // Define custom templates
    c.templates.set('varify/controls/polyphen', polyphen);
    c.templates.set('varify/controls/sift', sift);

    c.templates.set('varify/export/dialog', exportDialog);

    c.templates.set('varify/modals/phenotype', phenotype);
    c.templates.set('varify/modals/result', result);
    c.templates.set('varify/modals/sample', sample);

    c.templates.set('varify/sample/loader', sampleLoader);
    c.templates.set('varify/sample/row', sampleRow);
    c.templates.set('varify/sample/table', sampleTable);

    c.templates.set('varify/tables/header', header);

    c.templates.set('varify/variant/article-item', articleItem);
    c.templates.set('varify/variant/article-group', articleGroup);
    c.templates.set('varify/variant/articles', variantArticles);
    c.templates.set('varify/variant/assessment-metrics/percentages',
        metricsPercentages);
    c.templates.set('varify/variant/assessment-metrics/percentage-item',
        metricsPercentageItem);
    c.templates.set('varify/variant/assessment-metrics/user-popover-item',
        userPopoverItem);
    c.templates.set('varify/variant/assessment-metrics', assessmentMetrics);
    c.templates.set('varify/variant/cohort-item', cohortItem);
    c.templates.set('varify/variant/cohort-popover-item', cohortPopoverItem);
    c.templates.set('varify/variant/cohorts', variantCohorts);
    c.templates.set('varify/variant/effect-item', effectItem);
    c.templates.set('varify/variant/effect-type', effectType);
    c.templates.set('varify/variant/effects', variantEffects);
    c.templates.set('varify/variant/frequencies', variantFrequencies);
    c.templates.set('varify/variant/phenotype-item', phenotypeItem);
    c.templates.set('varify/variant/phenotype-group', phenotypeGroup);
    c.templates.set('varify/variant/phenotypes', variantPhenotypes);
    c.templates.set('varify/variant/scores', variantScores);
    c.templates.set('varify/variant/clinvar', clinvar);
    c.templates.set('varify/variant/clinvar-item', clinvarItem);
    c.templates.set('varify/variant/summary', variantSummary);

    c.templates.set('varify/workflows/results', results);
});
