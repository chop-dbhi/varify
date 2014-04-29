/* global define */

define([
    'underscore',
    './modals/result',
    './modals/phenotype',
    './modals/sample'
], function(_) {

    var mods = [].slice.call(arguments, 1);

    return _.extend.apply(null, [{}].concat(mods));

});
