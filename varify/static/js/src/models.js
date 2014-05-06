/* global define */

define([
    'underscore',
    './models/result',
    './models/assessment',
    './models/phenotype',
    './models/sample',
    './models/variant'
], function(_) {

    var mods = [].slice.call(arguments, 1);

    return _.extend.apply(null, [{}].concat(mods));
});
