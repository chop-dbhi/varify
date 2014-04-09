/* global define */

define([
    'underscore',
    './analysis/item',
    './analysis/list'
], function(_) {

    var mods = [].slice.call(arguments, 1);

    return _.extend.apply(null, [{}].concat(mods));

});
