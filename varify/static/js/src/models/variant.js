/* global define */

define([
    'underscore',
    'backbone',
    '../utils'
], function(_, Backbone, utils) {

    var Variant = Backbone.Model.extend({
        constructor: function(attrs, options) {
            // Force a parse to occur
            options = _.defaults({parse: true}, options);

            this.effects = new Backbone.Collection();
            this.phenotypes = new Backbone.Collection();
            this.cohorts = new Backbone.Collection();
            this.articles = new Backbone.Collection();
            this.clinvarResults = new Backbone.Collection();
            this.assessmentMetrics = new Backbone.Collection();

            Backbone.Model.prototype.constructor.call(this, attrs, options);
        },

        parse: function(attrs) {
            this.effects.reset(
                utils.groupEffectsByType(
                    _.filter(attrs.effects, function(effect) {
                        return effect.transcript !== null;
                    })
                )
            );

            this.phenotypes.reset(utils.groupPhenotypesByType(attrs));
            this.cohorts.reset(attrs.cohorts);
            this.articles.reset(utils.groupArticlesByType(attrs));

            var clinvarResults;
            if (attrs.solvebio && attrs.solvebio.clinvar) {
                clinvarResults = attrs.solvebio.clinvar.results;
            }
            this.clinvarResults.reset(clinvarResults);

            return attrs;
        }
    });

    return {
        Variant: Variant
    };

});
