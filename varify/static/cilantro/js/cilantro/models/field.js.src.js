var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', 'backbone', '../core', './base', './stats'], function(_, Backbone, c, base, stats) {
  var FieldCollection, FieldModel, getLogicalType, _ref;
  getLogicalType = function(attrs) {
    var type;
    if ((type = c.config.get("fields.instances." + attrs.id + ".type"))) {
      return type;
    }
    if (attrs.logical_type != null) {
      return attrs.logical_type;
    }
    type = attrs.simple_type;
    if (attrs.enumerable || type === 'boolean') {
      return 'choice';
    }
    return type;
  };
  FieldModel = (function(_super) {
    __extends(FieldModel, _super);

    function FieldModel() {
      var _this = this;
      FieldModel.__super__.constructor.apply(this, arguments);
      if (this.links.stats) {
        this.stats = new stats.StatCollection;
        this.stats.url = function() {
          return _this.links.stats;
        };
      }
    }

    FieldModel.prototype.parse = function() {
      var attrs;
      this._cache = {};
      attrs = FieldModel.__super__.parse.apply(this, arguments);
      attrs.type = getLogicalType(attrs);
      return attrs;
    };

    FieldModel.prototype.distribution = function(handler, cache) {
      var _this = this;
      if (cache == null) {
        cache = true;
      }
      if (this.links.distribution == null) {
        handler();
      }
      if (cache && (this._cache.distribution != null)) {
        handler(this._cache.distribution);
      } else {
        Backbone.ajax({
          url: this.links.distribution,
          dataType: 'json',
          success: function(resp) {
            _this._cache.distribution = cache ? resp : null;
            return handler(resp);
          }
        });
      }
    };

    FieldModel.prototype.values = function(params, handler, cache) {
      var deferred,
        _this = this;
      if (cache == null) {
        cache = true;
      }
      if (typeof params === 'function') {
        handler = params;
        cache = handler;
        params = {};
      } else if (params) {
        cache = false;
        if (typeof params === 'string') {
          params = {
            query: params
          };
        }
      }
      if (this.links.values == null) {
        handler();
      }
      deferred = Backbone.$.Deferred();
      if (handler) {
        deferred.done(handler);
      }
      if (cache && (this._cache.values != null)) {
        deferred.resolve(this._cache.values);
      } else {
        Backbone.ajax({
          url: this.links.values,
          data: params,
          dataType: 'json',
          success: function(resp) {
            if (cache) {
              _this._cache.values = resp;
            }
            return deferred.resolve(resp);
          },
          error: function() {
            return deferred.reject();
          }
        });
      }
      return deferred.promise();
    };

    return FieldModel;

  })(base.Model);
  FieldCollection = (function(_super) {
    __extends(FieldCollection, _super);

    function FieldCollection() {
      _ref = FieldCollection.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    FieldCollection.prototype.model = FieldModel;

    FieldCollection.prototype.search = function(query, handler) {
      return Backbone.ajax({
        url: _.result(this, 'url'),
        data: {
          query: query
        },
        dataType: 'json',
        success: function(resp) {
          return handler(resp);
        }
      });
    };

    return FieldCollection;

  })(base.Collection);
  return {
    FieldModel: FieldModel,
    FieldCollection: FieldCollection
  };
});
