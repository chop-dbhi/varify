/* global define */

define([
    'underscore',
    './workflows/results'
], function(_) {

    var mods = [].slice.call(arguments, 1);

    return _.extend.apply(null, [{}].concat(mods));

});
