var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['backbone'], function(Backbone) {
  var Collection, Model, SessionCollection, SynclessCollection, SynclessModel, _ref, _ref1, _ref2;
  Model = (function(_super) {
    __extends(Model, _super);

    Model.prototype.url = function() {
      if (this.isNew()) {
        return Model.__super__.url.apply(this, arguments);
      } else {
        return this.links.self;
      }
    };

    function Model(attrs, options) {
      this.links = {};
      Model.__super__.constructor.call(this, attrs, options);
      this.on('change:_links', function(model, attrs, options) {
        return this._parseLinks(attrs);
      });
    }

    Model.prototype._parseLinks = function(attrs) {
      var link, links, name;
      links = {};
      for (name in attrs) {
        link = attrs[name];
        links[name] = link.href;
      }
      return this.links = links;
    };

    Model.prototype.parse = function(attrs) {
      if ((attrs != null ? attrs._links : void 0) != null) {
        this._parseLinks(attrs._links);
      }
      return attrs;
    };

    return Model;

  })(Backbone.Model);
  Collection = (function(_super) {
    __extends(Collection, _super);

    Collection.prototype.model = Model;

    Collection.prototype.url = function() {
      return this.links.self;
    };

    function Collection(attrs, options) {
      this.links = {};
      Collection.__super__.constructor.call(this, attrs, options);
    }

    Collection.prototype._parseLinks = function(attrs) {
      var link, links, name;
      links = {};
      for (name in attrs) {
        link = attrs[name];
        links[name] = link.href;
      }
      return this.links = links;
    };

    Collection.prototype.parse = function(attrs) {
      if ((attrs != null ? attrs._links : void 0) != null) {
        this._parseLinks(attrs._links);
      }
      return attrs;
    };

    return Collection;

  })(Backbone.Collection);
  SynclessModel = (function(_super) {
    __extends(SynclessModel, _super);

    function SynclessModel() {
      _ref = SynclessModel.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    SynclessModel.prototype.sync = function() {};

    return SynclessModel;

  })(Model);
  SynclessCollection = (function(_super) {
    __extends(SynclessCollection, _super);

    function SynclessCollection() {
      _ref1 = SynclessCollection.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    SynclessCollection.prototype.sync = function() {};

    return SynclessCollection;

  })(Collection);
  SessionCollection = (function(_super) {
    __extends(SessionCollection, _super);

    function SessionCollection() {
      _ref2 = SessionCollection.__super__.constructor.apply(this, arguments);
      return _ref2;
    }

    SessionCollection.prototype.initialize = function() {
      this.add({
        session: true
      });
      return this.session = this.get('session');
    };

    SessionCollection.prototype._resetSession = function() {
      this.session.clear({
        silent: true
      });
      return this.session.set('session', true, {
        silent: true
      });
    };

    SessionCollection.prototype.reset = function(models, options) {
      var model, _i, _len, _ref3;
      if (options == null) {
        options = {};
      }
      _ref3 = this.models;
      for (_i = 0, _len = _ref3.length; _i < _len; _i++) {
        model = _ref3[_i];
        if (model === this.session) {
          this._resetSession();
        } else {
          this._removeReference(model);
        }
      }
      options.previousModels = this.models;
      this._reset();
      this.add(this.session, _.extend({
        silent: true
      }, options));
      if ((model = _.findWhere(models, {
        session: true
      }))) {
        this.session.set(model, options);
      }
      this.add(models, _.extend({
        silent: true,
        merge: true
      }, options));
      if (!options.silent) {
        this.trigger('reset', this, options);
      }
      return this;
    };

    SessionCollection.prototype.get = function(attrs) {
      var session;
      session = false;
      if (attrs instanceof Backbone.Model) {
        session = attrs.get('session');
      }
      if (attrs === 'session' || (typeof attrs === 'object' && attrs.session)) {
        session = true;
      }
      if (session) {
        return this.findWhere({
          session: true
        });
      } else {
        return SessionCollection.__super__.get.call(this, attrs);
      }
    };

    SessionCollection.prototype.getSession = function() {
      return this.session;
    };

    return SessionCollection;

  })(Collection);
  return {
    Model: Model,
    Collection: Collection,
    SynclessModel: SynclessModel,
    SynclessCollection: SynclessCollection,
    SessionCollection: SessionCollection
  };
});
