/* global define */

define([
    'cilantro',
    'tpl!../../../templates/analysis/assessment-item.html',
    'tpl!../../../templates/analysis/assessment-list.html',
    'tpl!../../../templates/analysis/item.html',
    'tpl!../../../templates/analysis/list.html',
    'tpl!../../../templates/controls/polyphen.html',
    'tpl!../../../templates/controls/sift.html',
    'tpl!../../../templates/export/dialog.html',
    'tpl!../../../templates/modals/phenotypes.html',
    'tpl!../../../templates/modals/result.html',
    'tpl!../../../templates/sample/loader.html',
    'tpl!../../../templates/tables/header.html',
    'tpl!../../../templates/workflows/analysis.html',
    'tpl!../../../templates/workflows/results.html'
], function(c, assessmentItem, assessmentList, analysisItem, analysisList,
            polyphen, sift, exportDialog, phenotype, result, sampleLoader,
            header, analysis, results) {

    // Define custom templates
    c.templates.set('varify/analysis/assessment-item', assessmentItem);
    c.templates.set('varify/analysis/assessment-list', assessmentList);
    c.templates.set('varify/analysis/item', analysisItem);
    c.templates.set('varify/analysis/list', analysisList);
    c.templates.set('varify/controls/polyphen', polyphen);
    c.templates.set('varify/controls/sift', sift);
    c.templates.set('varify/export/dialog', exportDialog);
    c.templates.set('varify/modals/phenotype', phenotype);
    c.templates.set('varify/modals/result', result);
    c.templates.set('varify/sample/loader', sampleLoader);
    c.templates.set('varify/tables/header', header);
    c.templates.set('varify/workflows/analysis', analysis);
    c.templates.set('varify/workflows/results', results);

});
