/* global define */

define([
    'backbone',
    '../utils'
], function(Backbone, utils) {

    var Phenotype = Backbone.Model.extend({
        urlRoot: function() {
            var path = 'api/samples/' + this.get('sample_id') + '/phenotypes';
            return utils.toAbsolutePath(path);
        }
    });

    return {
        Phenotype: Phenotype
    };
});
