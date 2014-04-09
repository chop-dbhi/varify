/* global define */

define([
    'backbone'
], function(Backbone) {

    var Sample = Backbone.Model.extend({
        url: function() {
            return '/api/samples/' + this.get('id') + '/';
        }
    });

    return {
        Sample: Sample
    };

});
