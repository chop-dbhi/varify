var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', 'backbone'], function(_, Backbone) {
  var StatCollection, StatModel;
  StatModel = (function(_super) {
    __extends(StatModel, _super);

    function StatModel() {
      return StatModel.__super__.constructor.apply(this, arguments);
    }

    StatModel.prototype.idAttribute = 'key';

    return StatModel;

  })(Backbone.Model);
  StatCollection = (function(_super) {
    __extends(StatCollection, _super);

    function StatCollection() {
      return StatCollection.__super__.constructor.apply(this, arguments);
    }

    StatCollection.prototype.model = StatModel;

    StatCollection.prototype.parse = function(attrs) {
      var key, stats, value;
      stats = [];
      for (key in attrs) {
        value = attrs[key];
        if (key.slice(0, 1) === '_') {
          continue;
        }
        stats.push({
          key: key,
          value: value
        });
      }
      return stats;
    };

    return StatCollection;

  })(Backbone.Collection);
  return {
    StatModel: StatModel,
    StatCollection: StatCollection
  };
});
