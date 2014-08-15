/* global define */

define([
    'backbone',
    '../utils'
], function(Backbone, utils) {

    var SampleVariantSet = Backbone.Model.extend({

    });


    var SampleVariantSets = Backbone.Collection.extend({
        model: SampleVariantSet
    });


    var Sample = Backbone.Model.extend({
        url: function() {
            return utils.toAbsolutePath('api/samples/' + this.get('id') + '/');
        },

        constructor: function() {
            this.variantSets = new SampleVariantSets();

            var _this = this;
            this.variantSets.url = function() {
                return _this.url() + 'variants/sets/';
            };

            Backbone.Model.prototype.constructor.apply(this, arguments);
        }
    });


    var Samples = Backbone.Collection.extend({
        model: Sample,

        url: function() {
            return utils.toAbsolutePath('api/samples/');
        }
    });


    return {
        Sample: Sample,
        Samples: Samples
    };

});
