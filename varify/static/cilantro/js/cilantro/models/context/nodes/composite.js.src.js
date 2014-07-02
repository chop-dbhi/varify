var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['./base'], function(base) {
  var CompositeNodeModel, _ref;
  CompositeNodeModel = (function(_super) {
    __extends(CompositeNodeModel, _super);

    function CompositeNodeModel() {
      _ref = CompositeNodeModel.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    CompositeNodeModel.prototype.type = 'composite';

    CompositeNodeModel.prototype.validate = function(attrs) {
      if (attrs.composite == null) {
        return 'Not a valid composite node';
      }
    };

    return CompositeNodeModel;

  })(base.ContextNodeModel);
  return {
    CompositeNodeModel: CompositeNodeModel
  };
});
