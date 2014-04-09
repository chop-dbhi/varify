/* global define */

define([
    'underscore',
    './models/result',
    './models/assessment',
    './models/phenotype',
    './models/sample'
], function(_) {

    var mods = [].slice.call(arguments, 1);

    return _.extend.apply(null, [{}].concat(mods));
});
