/* global define */

define([
    'underscore',
    './models/result',
    './models/assessment',
    './models/phenotype'
], function(_) {

    // Modules to be mixed-in with exports
    var mods = Array.prototype.slice.call(arguments, 1);

    return $.extend.apply(null, mods);
});
