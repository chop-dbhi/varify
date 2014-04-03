var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', 'backbone', '../core', './base'], function(_, Backbone, c, base) {
  var Facet, Facets, ViewCollection, ViewModel, _ref, _ref1, _ref2;
  Facet = (function(_super) {
    __extends(Facet, _super);

    function Facet() {
      _ref = Facet.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    Facet.prototype.idAttribute = 'concept';

    return Facet;

  })(Backbone.Model);
  Facets = (function(_super) {
    __extends(Facets, _super);

    function Facets() {
      _ref1 = Facets.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    Facets.prototype.model = Facet;

    return Facets;

  })(Backbone.Collection);
  ViewModel = (function(_super) {
    __extends(ViewModel, _super);

    function ViewModel() {
      this.facets = new Facets;
      this.on('change:json', function(model, value, options) {
        return this.jsonToFacets(value);
      });
      ViewModel.__super__.constructor.apply(this, arguments);
    }

    ViewModel.prototype.initialize = function() {
      var _this = this;
      this.on('request', function() {
        return c.trigger(c.VIEW_SYNCING, this);
      });
      this.on('sync', function(model, attrs, options) {
        if (options == null) {
          options = {};
        }
        if (options.silent !== true) {
          return c.trigger(c.VIEW_SYNCED, this, 'success');
        }
      });
      this.on('error', function() {
        return c.trigger(c.VIEW_SYNCED, this, 'error');
      });
      this.on('change', function() {
        return c.trigger(c.VIEW_CHANGED, this);
      });
      return c.on(c.VIEW_SAVE, function(id) {
        if (_this.id === id || !id && _this.isSession()) {
          return _this.save();
        }
      });
    };

    ViewModel.prototype.isSession = function() {
      return this.get('session');
    };

    ViewModel.prototype.isArchived = function() {
      return this.get('archived');
    };

    ViewModel.prototype.toJSON = function() {
      var attrs;
      attrs = ViewModel.__super__.toJSON.apply(this, arguments);
      attrs.json = this.facetsToJSON();
      return attrs;
    };

    ViewModel.prototype.parse = function(attrs) {
      ViewModel.__super__.parse.apply(this, arguments);
      this.jsonToFacets(attrs.json);
      return attrs;
    };

    ViewModel.prototype.jsonToFacets = function(json) {
      var attrs, columns, i, id, models, ordering, sort, _i, _id, _j, _len, _len1, _ref2;
      if (_.isArray(json)) {
        this.facets.reset(json);
        return;
      }
      models = [];
      columns = json.columns || [];
      ordering = json.ordering || [];
      for (_i = 0, _len = columns.length; _i < _len; _i++) {
        id = columns[_i];
        attrs = {
          concept: id
        };
        for (i = _j = 0, _len1 = ordering.length; _j < _len1; i = ++_j) {
          _ref2 = ordering[i], _id = _ref2[0], sort = _ref2[1];
          if (id === _id) {
            attrs.sort = sort;
            attrs.sort_index = i;
          }
        }
        models.push(attrs);
      }
      return this.facets.reset(models);
    };

    ViewModel.prototype.facetsToJSON = function() {
      var json;
      json = {
        ordering: [],
        columns: []
      };
      this.facets.each(function(model) {
        var direction, index, sort;
        json.columns.push(model.get('concept'));
        if ((direction = model.get('sort'))) {
          index = model.get('sort_index');
          sort = [model.get('concept'), direction];
          return json.ordering.splice(index, 0, sort);
        }
      });
      return json;
    };

    return ViewModel;

  })(base.Model);
  ViewCollection = (function(_super) {
    __extends(ViewCollection, _super);

    function ViewCollection() {
      _ref2 = ViewCollection.__super__.constructor.apply(this, arguments);
      return _ref2;
    }

    ViewCollection.prototype.model = ViewModel;

    return ViewCollection;

  })(base.SessionCollection);
  return {
    ViewModel: ViewModel,
    ViewCollection: ViewCollection
  };
});
