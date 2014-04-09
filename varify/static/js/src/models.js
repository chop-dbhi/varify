/* global define */

define([
    'underscore',
    './models/analysis',
    './models/assessment',
    './models/phenotype',
    './models/result',
    './models/sample'
], function(_) {

    var mods = [].slice.call(arguments, 1);

    return _.extend.apply(null, [{}].concat(mods));
});
