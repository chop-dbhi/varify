/* global define */

define([
    'underscore',
    './ui/controls',
    './ui/modals',
    './ui/tables',
    './ui/workflows'
], function(_) {

    // Modules to be mixed-in with exports
    var mods = Array.prototype.slice.call(arguments, 1);

    return _.extend.apply(null, mods);
});
