/* global define */

define([
    'underscore',
    './tables/body',
    './tables/header',
    './tables/row',
    './tables/table'
], function() {

    var mods = [].slice.call(arguments, 1);

    return _.extend.apply(null, [{}].concat(mods));

});
