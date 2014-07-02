var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  __slice = [].slice;

define(['underscore', 'backbone', './base'], function(_, Backbone, base) {
  var BranchNodeModel, ContextNodeCollection;
  ContextNodeCollection = (function(_super) {
    __extends(ContextNodeCollection, _super);

    function ContextNodeCollection(models, options) {
      ContextNodeCollection.__super__.constructor.call(this, models, options);
      this.parent = options != null ? options.parent : void 0;
    }

    ContextNodeCollection.prototype.model = function(attrs, options) {
      return base.ContextNodeModel.create(attrs, options);
    };

    ContextNodeCollection.prototype.get = function(attrs) {
      if (typeof attrs === 'number' || (attrs.id != null)) {
        return ContextNodeCollection.__super__.get.call(this, attrs);
      }
      if (attrs instanceof base.ContextNodeModel) {
        attrs = attrs.identity();
      } else {
        attrs = _.pick(attrs, this.parent.identKeys);
      }
      return this.find(attrs);
    };

    ContextNodeCollection.prototype.set = function(models, options) {
      var model, _i, _len;
      if (models == null) {
        return ContextNodeCollection.__super__.set.call(this, null, options);
      }
      if (!_.isArray(models)) {
        models = [models];
      }
      for (_i = 0, _len = models.length; _i < _len; _i++) {
        model = models[_i];
        if (model === this.parent) {
          throw new base.ContextNodeError('Cannot add self as child');
        }
      }
      return ContextNodeCollection.__super__.set.call(this, models, options);
    };

    ContextNodeCollection.prototype.find = function(ident, options) {
      var child, node, _i, _len, _ref;
      _ref = this.models;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        child = _ref[_i];
        if ((node = child.find(ident, options))) {
          return node;
        }
      }
    };

    return ContextNodeCollection;

  })(Backbone.Collection);
  BranchNodeModel = (function(_super) {
    __extends(BranchNodeModel, _super);

    BranchNodeModel.prototype.type = 'branch';

    BranchNodeModel.prototype.defaults = function() {
      return {
        type: 'and',
        children: []
      };
    };

    function BranchNodeModel() {
      var _this = this;
      this.children = new ContextNodeCollection(null, {
        parent: this
      });
      this.on('change:children', function(model, value, options) {
        return this.children.set(value, options);
      });
      this.on('clear', function() {
        var model, _i, _len, _ref, _results;
        _ref = this.children.models;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          model = _ref[_i];
          _results.push(model.trigger('clear'));
        }
        return _results;
      });
      this.children.on('change', function() {
        var args;
        args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
        _this.set('children', _this.children.toJSON(), {
          silent: true
        });
        return _this.trigger.apply(_this, ['change'].concat(__slice.call(args)));
      });
      BranchNodeModel.__super__.constructor.apply(this, arguments);
    }

    BranchNodeModel.prototype.toJSON = function(options) {
      var attrs, child, children, _i, _len, _ref;
      children = [];
      _ref = this.children.models;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        child = _ref[_i];
        if (child.isValid(options) && (attrs = child.toJSON(options))) {
          children.push(attrs);
        }
      }
      if (!children.length) {
        return;
      }
      (attrs = BranchNodeModel.__super__.toJSON.apply(this, arguments)).children = children;
      return attrs;
    };

    BranchNodeModel.prototype._validate = function(attrs, options) {
      var error;
      if (!options.validate) {
        return true;
      }
      if (!attrs || _.isEmpty(attrs)) {
        attrs = this.toJSON(options);
      }
      attrs = _.extend({}, attrs);
      error = this.validationError = this.validate(attrs, options) || null;
      if (!error) {
        return true;
      }
      this.trigger('invalid', this, error, _.extend(options, {
        validationError: error
      }));
      return false;
    };

    BranchNodeModel.prototype.validate = function(attrs, options) {
      if (!(attrs.type === 'and' || attrs.type === 'or')) {
        return 'Not a valid branch type';
      }
      if (!attrs.children.length) {
        return 'No children present';
      }
    };

    BranchNodeModel.prototype.define = function(attrs, path, options) {
      var child, ident, parent, _i, _len;
      if (!path || !_.isArray(path)) {
        options = path;
        path = [];
      }
      options = _.extend({
        manager: this.manager,
        identKeys: this.identKeys
      }, options);
      parent = this;
      for (_i = 0, _len = path.length; _i < _len; _i++) {
        ident = path[_i];
        if (!(child = parent.find(ident))) {
          parent.children.add(ident, {
            type: 'branch'
          });
          child = parent.children.find(ident);
        }
        if (child.type !== 'branch') {
          throw new Error('Cannot define node in non-branch');
        }
        parent = child;
      }
      parent.children.add(attrs, options);
      return parent.find(_.pick(attrs, options.identKeys));
    };

    BranchNodeModel.prototype.find = function(ident, options) {
      var node;
      if ((node = BranchNodeModel.__super__.find.call(this, ident, options))) {
        return node;
      }
      return this.children.find(ident, options);
    };

    BranchNodeModel.prototype.clear = function(options) {
      if (options == null) {
        options = {};
      }
      this.children.each(function(model) {
        return model.clear(options);
      });
      if (options.reset) {
        this.children.reset();
      }
    };

    return BranchNodeModel;

  })(base.ContextNodeModel);
  return {
    BranchNodeModel: BranchNodeModel
  };
});
