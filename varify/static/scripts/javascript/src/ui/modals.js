/* global define */

define([
    'underscore',
    './modals/result',
    './modals/phenotype'
], function() {

    var mods = [].slice.call(arguments, 1);

    return _.extend.apply(null, [{}].concat(mods));

});
