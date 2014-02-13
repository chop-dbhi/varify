// Generated by CoffeeScript 1.7.1
var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', 'backbone', '../utils'], function(_, Backbone, utils) {
  var Result;
  Result = (function(_super) {
    __extends(Result, _super);

    function Result() {
      return Result.__super__.constructor.apply(this, arguments);
    }

    Result.prototype.url = function() {
      return "" + (utils.getRootUrl()) + "api/samples/variants/" + this.id + "/";
    };

    Result.prototype.parse = function(attrs) {
      var genes, uniqueGenes, variant;
      variant = attrs.variant;
      variant.effects = _.sortBy(variant.effects, function(eff) {
        return utils.effectImpactPriority(eff.impact);
      });
      uniqueGenes = {};
      genes = [];
      _.each(variant.effects, function(eff) {
        var gene;
        if (!eff.transcript || !(gene = eff.transcript.gene)) {
          return;
        }
        if (/^LOC\d+/.test(gene.symbol) || (uniqueGenes[gene.symbol] != null)) {
          return;
        }
        uniqueGenes[gene.symbol] = true;
        return genes.push({
          symbol: gene.symbol,
          hgnc_id: gene.hgnc_id,
          name: gene.name
        });
      });
      variant.uniqueGenes = genes;
      return attrs;
    };

    return Result;

  })(Backbone.Model);
  return {
    Result: Result
  };
});
