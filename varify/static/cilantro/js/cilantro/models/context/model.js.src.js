var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  __slice = [].slice;

define(['../../core', '../base', './manager', './nodes'], function(c, base, manager, nodes) {
  var ContextCollection, ContextModel, contextNodeModels, getContextNodeType, _ref, _ref1;
  contextNodeModels = {
    branch: nodes.BranchNodeModel,
    condition: nodes.ConditionNodeModel,
    composite: nodes.CompositeNodeModel
  };
  getContextNodeType = function(attrs, options) {
    var model, type;
    if (attrs instanceof nodes.ContextNodeModel) {
      return attrs.type;
    }
    for (type in contextNodeModels) {
      model = contextNodeModels[type];
      if (!model.prototype.validate.call(attrs, attrs, options)) {
        return type;
      }
    }
    return 'condition';
  };
  nodes.ContextNodeModel.create = function(attrs, options) {
    var klass, type;
    type = options.type || getContextNodeType(attrs, options);
    if ((klass = contextNodeModels[type]) == null) {
      throw new nodes.ContextNodeError('Unknown context node type');
    }
    return new klass(attrs, options);
  };
  ContextModel = (function(_super) {
    __extends(ContextModel, _super);

    function ContextModel() {
      _ref = ContextModel.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    ContextModel.prototype.managerEventPrefix = 'tree';

    ContextModel.prototype.initialize = function() {
      var _this = this;
      this.manager = new manager.ContextTreeManager(this);
      this.listenTo(this.manager, 'all', function() {
        var args, event, manager;
        manager = arguments[0], event = arguments[1], args = 3 <= arguments.length ? __slice.call(arguments, 2) : [];
        return _this.trigger.apply(_this, ["" + _this.managerEventPrefix + ":" + event].concat(__slice.call(args)));
      });
      this.on('sync', function(model, attrs, options) {
        if (options == null) {
          options = {};
        }
        if (options.silent !== true) {
          return c.trigger(c.CONTEXT_SYNCED, this, 'success');
        }
      });
      return this.on('change:json', function(model, value, options) {
        return this.manager.set(value, options);
      });
    };

    ContextModel.prototype.toJSON = function(options) {
      var attrs;
      if (options == null) {
        options = {};
      }
      attrs = ContextModel.__super__.toJSON.apply(this, arguments);
      attrs.json = this.manager.toJSON();
      return attrs;
    };

    ContextModel.prototype.isSession = function() {
      return this.get('session');
    };

    ContextModel.prototype.isArchived = function() {
      return this.get('archived');
    };

    return ContextModel;

  })(base.Model);
  ContextCollection = (function(_super) {
    __extends(ContextCollection, _super);

    function ContextCollection() {
      _ref1 = ContextCollection.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    ContextCollection.prototype.model = ContextModel;

    return ContextCollection;

  })(base.SessionCollection);
  return {
    ContextModel: ContextModel,
    ContextCollection: ContextCollection
  };
});
