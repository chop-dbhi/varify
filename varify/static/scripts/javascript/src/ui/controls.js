/* global define */

define([
    'underscore',
    './controls/sift',
    './controls/polyphen'
], function() {

    var mods = [].slice.call(arguments, 1);

    return _.extend.apply(null, [{}].concat(mods));
});
