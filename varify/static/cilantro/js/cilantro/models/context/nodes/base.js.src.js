var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', 'backbone', '../../base'], function(_, Backbone, base) {
  var ContextNodeError, ContextNodeModel, _ref;
  ContextNodeError = (function(_super) {
    __extends(ContextNodeError, _super);

    function ContextNodeError() {
      _ref = ContextNodeError.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    return ContextNodeError;

  })(Error);
  /*
  Base context node model containing basic validation, identity functions,
  and setting common elements. This is a _syncless_ model since it itself
  does not sync with the server, but is a component of an upstream structure.
  */

  ContextNodeModel = (function(_super) {
    __extends(ContextNodeModel, _super);

    function ContextNodeModel(attrs, options) {
      if (options == null) {
        options = {};
      }
      options = _.extend({
        identKeys: ['concept', 'field', 'operator']
      }, options);
      this.manager = options.manager;
      this.identKeys = options.identKeys;
      ContextNodeModel.__super__.constructor.call(this, attrs, options);
    }

    ContextNodeModel.prototype.identity = function() {
      return this.pick.apply(this, this.identKeys);
    };

    ContextNodeModel.prototype.path = function() {
      var ident, node, path, _ref1;
      path = [];
      node = this;
      while (true) {
        if ((node = (_ref1 = node.collection) != null ? _ref1.parent : void 0) && !_.isEmpty((ident = node.identity()))) {
          path.unshift(ident);
        } else {
          break;
        }
      }
      return path;
    };

    ContextNodeModel.prototype.validate = function(attrs, options) {
      var error, model;
      try {
        model = ContextNodeModel.create(attrs, options);
        if (!model.isValid(options)) {
          return model.validationError;
        }
      } catch (_error) {
        error = _error;
        return error.message;
      }
    };

    ContextNodeModel.prototype.clear = function() {
      var attrs;
      attrs = this.identity();
      ContextNodeModel.__super__.clear.apply(this, arguments);
      return this.set(attrs, {
        silent: true
      });
    };

    ContextNodeModel.prototype.destroy = function(options) {
      return this.trigger('destroy', this, this.collection, options);
    };

    ContextNodeModel.prototype.find = function(ident, options) {
      var key, match, value;
      if (options == null) {
        options = {};
      }
      if (_.isEmpty(ident)) {
        return false;
      }
      for (key in ident) {
        value = ident[key];
        if (!_.isEqual(this.get(key), value)) {
          match = false;
          break;
        }
      }
      if (match !== false) {
        return this;
      }
    };

    ContextNodeModel.prototype.apply = function(options) {
      if (!this.isValid(options)) {
        return false;
      }
      return this.manager.apply(this, options);
    };

    ContextNodeModel.prototype.remove = function(options) {
      return this.manager.remove(this, options);
    };

    ContextNodeModel.prototype.revert = function(options) {
      return this.manager.revert(this, options);
    };

    ContextNodeModel.prototype.enable = function(options) {
      return this.manager.enable(this, options);
    };

    ContextNodeModel.prototype.disable = function(options) {
      return this.manager.disable(this, options);
    };

    ContextNodeModel.prototype.toggleEnabled = function(options) {
      var enabled;
      if ((enabled = this.isEnabled(options))) {
        this.disable(options);
      } else {
        this.enable(options);
      }
      return !enabled;
    };

    ContextNodeModel.prototype.isNew = function(options) {
      return this.manager.isNew(this, options);
    };

    ContextNodeModel.prototype.isDirty = function(options) {
      return this.manager.isDirty(this, options);
    };

    ContextNodeModel.prototype.isEnabled = function(options) {
      return this.manager.isEnabled(this, options);
    };

    return ContextNodeModel;

  })(base.SynclessModel);
  return {
    ContextNodeError: ContextNodeError,
    ContextNodeModel: ContextNodeModel
  };
});
