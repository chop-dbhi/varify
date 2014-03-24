/* global define */

define([
    'underscore',
    './modals/result'
], function() {

    var mods = [].slice.call(arguments, 1);

    return _.extend.apply(null, [{}].concat(mods));

});
