/* global define */

define([
    'underscore',
    './variant/articles',
    './variant/assessment-metrics',
    './variant/solvebio',
    './variant/cohorts',
    './variant/effects',
    './variant/frequencies',
    './variant/phenotypes',
    './variant/scores',
    './variant/summary',
], function(_) {

    var mods = [].slice.call(arguments, 1);

    return _.extend.apply(null, [{}].concat(mods));

});
