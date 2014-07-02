var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', './base'], function(_, base) {
  var ConditionNodeModel, _ref;
  ConditionNodeModel = (function(_super) {
    __extends(ConditionNodeModel, _super);

    function ConditionNodeModel() {
      _ref = ConditionNodeModel.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    ConditionNodeModel.prototype.type = 'condition';

    ConditionNodeModel.prototype.validate = function(attrs) {
      if (!((attrs.operator != null) && (attrs.field != null) && (attrs.value != null))) {
        return 'Not a valid condition node';
      }
      if (_.isArray(attrs.value) && !attrs.value.length) {
        return 'Empty condition value';
      }
      if (_.isArray(attrs.value) && attrs.operator === 'range') {
        if (attrs.value.length !== 2) {
          return 'Exactly 2 values must be supplied to define a range';
        }
        if (attrs.value[0] > attrs.value[1]) {
          return 'Lower bound value must be less than upper bound value';
        }
      }
    };

    ConditionNodeModel.prototype.toJSON = function(options) {
      var attrs;
      attrs = ConditionNodeModel.__super__.toJSON.call(this, options);
      if ((attrs.value != null) && typeof attrs.value === 'object') {
        attrs.value = _.clone(attrs.value);
      }
      return attrs;
    };

    return ConditionNodeModel;

  })(base.ContextNodeModel);
  return {
    ConditionNodeModel: ConditionNodeModel
  };
});
