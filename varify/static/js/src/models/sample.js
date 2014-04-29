/* global define */

define([
    'backbone'
], function(Backbone) {

    var Sample = Backbone.Model.extend({
        url: function() {
            return '/api/samples/' + this.get('id') + '/';
        }
    });


    var Samples = Backbone.Collection.extend({
        model: Sample,

        url: function() {
            return '/api/samples/';
        }
    });


    return {
        Sample: Sample,
        Samples: Samples
    };

});
