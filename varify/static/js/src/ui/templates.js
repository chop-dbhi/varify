/* global define */

define([
    'cilantro',
    'tpl!../../../templates/tables/header.html',
    'tpl!../../../templates/modals/result.html',
    'tpl!../../../templates/modals/phenotypes.html',
    'tpl!../../../templates/controls/sift.html',
    'tpl!../../../templates/controls/polyphen.html',
    'tpl!../../../templates/workflows/results.html',
    'tpl!../../../templates/export/dialog.html',
    'tpl!../../../templates/sample/loader.html'
], function(c, header, result, phenotype, sift, polyphen, results,
            exportDialog, sampleLoader) {

    // Define custom templates
    c.templates.set('varify/export/dialog', exportDialog);
    c.templates.set('varify/tables/header', header);
    c.templates.set('varify/modals/result', result);
    c.templates.set('varify/modals/phenotype', phenotype);
    c.templates.set('varify/controls/sift', sift);
    c.templates.set('varify/controls/polyphen', polyphen);
    c.templates.set('varify/workflows/results', results);
    c.templates.set('varify/sample/loader', sampleLoader);

});
