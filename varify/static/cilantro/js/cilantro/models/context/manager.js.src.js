var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', 'backbone', '../../core', './nodes'], function(_, Backbone, c, nodes) {
  var ContextTreeManager, Evented;
  _.extend((Evented = (function() {
    function Evented() {}

    return Evented;

  })()).prototype, Backbone.Events);
  /*
  The context tree manager maintains two trees, `working` and `upstream`.
  The working tree contains the current state of all context nodes
  that have been interacted with during the session. The upstream tree
  contains nodes that were applied while in a valid state. When synced
  with the server, the upstream tree is serialized for use as the `json`
  property on the context model.
  
  All nodes defined by the manager contain a referecne to manager for
  proxying operations that rely on the working or upstream trees.
  
  Other notes:
  
  - On a successful sync with the server, the response is merged into both
  the working and upstream trees.
  - The manager never returns nodes from upstream for manipulation. Views
  that bind to the `upstream` node or descendents should use the exposed
  methods on upstream nodes.
  - `ident = ident.identity?() or ident` gets the identity of a node if passed
  */

  ContextTreeManager = (function(_super) {
    __extends(ContextTreeManager, _super);

    ContextTreeManager.prototype.options = {
      identKeys: ['concept', 'field', 'operator']
    };

    function ContextTreeManager(model, options) {
      this.model = model;
      this.options = _.extend({}, this.options, options);
      this.working = new nodes.BranchNodeModel(null, {
        manager: this
      });
      this.upstream = new nodes.BranchNodeModel(null, {
        manager: this
      });
      this.set(this.model.get('json'));
    }

    ContextTreeManager.prototype.toJSON = function() {
      return this.upstream.toJSON();
    };

    ContextTreeManager.prototype._getRequired = function() {
      return c.config.get('query.concepts.required', []);
    };

    ContextTreeManager.prototype._isRequired = function(node) {
      var id;
      id = node.get('concept');
      return this._getRequired().indexOf(id) > -1;
    };

    ContextTreeManager.prototype._triggerRequired = function(required) {
      var id;
      return c.trigger(c.CONTEXT_REQUIRED, (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = required.length; _i < _len; _i++) {
          id = required[_i];
          _results.push({
            concept: id,
            reason: 'required'
          });
        }
        return _results;
      })());
    };

    ContextTreeManager.prototype._checkRequired = function() {
      var id, invalid, n, reason, _i, _len, _ref, _ref1, _ref2;
      invalid = [];
      _ref = this._getRequired();
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        id = _ref[_i];
        if (!(n = this.find({
          concept: id
        }))) {
          reason = 'undefined';
        } else if (!n.isValid()) {
          reason = 'invalid';
        } else if (n.get('enabled') === false) {
          reason = 'disabled';
        }
        if (reason) {
          invalid.push({
            concept: id,
            reason: reason
          });
        }
      }
      if (invalid.length) {
        c.trigger(c.CONTEXT_INVALID, invalid);
        if ((_ref1 = c.session) != null) {
          _ref1.state.context_invalid = true;
        }
        return false;
      } else {
        if ((_ref2 = c.session) != null) {
          _ref2.state.context_invalid = void 0;
        }
      }
      return true;
    };

    ContextTreeManager.prototype._set = function(node, attrs, options) {
      if ((attrs.concept != null) || (attrs.field != null)) {
        return node.children.add(attrs, options);
      } else {
        return node.set(attrs, options);
      }
    };

    ContextTreeManager.prototype.set = function(attrs, options) {
      if (options == null) {
        options = {};
      }
      if (options.reset) {
        this.upstream.clear({
          reset: true
        });
        this.working.clear();
      }
      if (attrs == null) {
        return this.clear();
      }
      this._set(this.upstream, attrs, {
        manager: this,
        identKeys: this.options.identKeys,
        validate: false,
        remove: false
      });
      return this._set(this.working, attrs, {
        manager: this,
        identKeys: this.options.identKeys,
        validate: false,
        remove: false
      });
    };

    ContextTreeManager.prototype.find = function(ident, options) {
      ident = (typeof ident.identity === "function" ? ident.identity() : void 0) || ident;
      return this.working.find(ident, options);
    };

    ContextTreeManager.prototype.define = function(attrs, options) {
      return this.working.define(attrs, options);
    };

    ContextTreeManager.prototype.save = function(node, options) {
      var _this = this;
      if (node == null) {
        node = this.upstream;
      }
      options = _.extend({}, options, {
        beforeSend: function(xhr) {
          return node.trigger('request', node, xhr, options);
        }
      });
      return this.model.save(null, options).done(function(data, status, xhr) {
        return node.trigger('sync', node, node.toJSON(), options);
      }).fail(function(xhr, status, error) {
        return node.trigger('error', node, xhr, options);
      });
    };

    ContextTreeManager.prototype.remove = function(ident, options) {
      var n, u;
      ident = (typeof ident.identity === "function" ? ident.identity() : void 0) || ident;
      if (!(n = this.find(ident))) {
        return false;
      }
      if (this._isRequired(n)) {
        this._triggerRequired([n.get('concept')]);
        return false;
      }
      if (!this._checkRequired()) {
        return false;
      }
      if ((u = this.upstream.find(ident))) {
        u.destroy();
        n.trigger('remove');
        u.trigger('remove');
        return this.save(n);
      }
    };

    ContextTreeManager.prototype.apply = function(ident, options) {
      var attrs, n, u;
      ident = (typeof ident.identity === "function" ? ident.identity() : void 0) || ident;
      if (!this._checkRequired()) {
        return false;
      }
      if (!(n = this.find(ident))) {
        return false;
      }
      if (!(attrs = n.toJSON())) {
        return false;
      }
      u = this.upstream.define(ident, n.path(), {
        type: n.type
      });
      u.set(attrs, options);
      if (u.hasChanged()) {
        n.trigger('apply');
        u.trigger('apply');
        return this.save(u);
      }
    };

    ContextTreeManager.prototype.revert = function(ident, options) {
      var n, u;
      ident = (typeof ident.identity === "function" ? ident.identity() : void 0) || ident;
      if (!(n = this.find(ident))) {
        return;
      }
      if ((u = this.upstream.find(ident))) {
        n.set(u.toJSON(), {
          remove: false
        });
        if (n.hasChanged()) {
          n.trigger('revert');
          return u.trigger('revert');
        }
      } else {
        return n.clear();
      }
    };

    ContextTreeManager.prototype.enable = function(ident) {
      var n, u;
      ident = (typeof ident.identity === "function" ? ident.identity() : void 0) || ident;
      if (!(n = this.find(ident))) {
        return;
      }
      if ((u = this.upstream.find(ident))) {
        u.set({
          enabled: true
        });
        if (u.hasChanged('enabled')) {
          n.trigger('enable');
          u.trigger('enable');
          return this.save(u);
        }
      }
    };

    ContextTreeManager.prototype.disable = function(ident) {
      var n, u;
      ident = (typeof ident.identity === "function" ? ident.identity() : void 0) || ident;
      if (!(n = this.find(ident))) {
        return false;
      }
      if (this._isRequired(n)) {
        this._triggerRequired([n.get('concept')]);
        return false;
      }
      if (!this._checkRequired()) {
        return false;
      }
      if ((u = this.upstream.find(ident))) {
        u.set({
          enabled: false
        });
        if (u.hasChanged('enabled')) {
          n.trigger('disable');
          u.trigger('disable');
          return this.save(u);
        }
      }
    };

    ContextTreeManager.prototype.clear = function(options) {
      var required;
      if (options == null) {
        options = {};
      }
      if ((required = this._getRequired()).length) {
        this._triggerRequired(required);
        return false;
      }
      this.upstream.clear({
        reset: true
      });
      this.upstream.trigger('clear');
      this.working.trigger('clear');
      if (this.upstream.hasChanged()) {
        return this.save();
      }
    };

    ContextTreeManager.prototype.isNew = function(ident) {
      ident = (typeof ident.identity === "function" ? ident.identity() : void 0) || ident;
      return !this.upstream.find(ident);
    };

    ContextTreeManager.prototype.isDirty = function(ident) {
      var u;
      ident = (typeof ident.identity === "function" ? ident.identity() : void 0) || ident;
      if (!(u = this.upstream.find(ident))) {
        return false;
      }
      return !_.isEqual(u.toJSON(), this.find(ident).toJSON());
    };

    ContextTreeManager.prototype.isEnabled = function(ident) {
      var node;
      ident = (typeof ident.identity === "function" ? ident.identity() : void 0) || ident;
      if ((node = this.upstream.find(ident))) {
        return node.get('enabled') !== false;
      }
      return false;
    };

    return ContextTreeManager;

  })(Evented);
  return {
    ContextTreeManager: ContextTreeManager
  };
});
