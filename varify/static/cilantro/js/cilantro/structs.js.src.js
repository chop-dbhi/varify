var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

define(['underscore', 'backbone', './models/base'], function(_, Backbone, base) {
  var Datum, Frame, FrameArray, Index, Indexes, Series, _DatumArray, _SeriesArray, _ref, _ref1;
  Index = (function(_super) {
    __extends(Index, _super);

    function Index() {
      _ref = Index.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    Index.prototype.defaults = {
      visible: true
    };

    Index.prototype.show = function() {
      return this.set({
        visible: true
      });
    };

    Index.prototype.hide = function() {
      return this.set({
        visible: false
      });
    };

    return Index;

  })(Backbone.Model);
  Indexes = (function(_super) {
    __extends(Indexes, _super);

    function Indexes() {
      _ref1 = Indexes.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    Indexes.prototype.model = Index;

    return Indexes;

  })(Backbone.Collection);
  Datum = (function(_super) {
    __extends(Datum, _super);

    function Datum(attrs, index, options) {
      if (!(index instanceof Index)) {
        index = new Index(index);
      }
      this.index = index;
      Datum.__super__.constructor.call(this, attrs, options);
    }

    Datum.prototype.size = function() {
      return 1;
    };

    Datum.prototype.width = function() {
      return 1;
    };

    return Datum;

  })(Backbone.Model);
  _DatumArray = (function(_super) {
    __extends(_DatumArray, _super);

    function _DatumArray(attrs, indexes, options) {
      this.model = __bind(this.model, this);
      this.indexes = indexes;
      _DatumArray.__super__.constructor.call(this, attrs, options);
    }

    _DatumArray.prototype.model = function(value, options) {
      var index;
      index = this.indexes.at(_.keys(this._byId).length);
      return new Datum({
        value: value
      }, index);
    };

    return _DatumArray;

  })(Backbone.Collection);
  Series = (function(_super) {
    __extends(Series, _super);

    function Series(attrs, indexes, options) {
      var data;
      if (options == null) {
        options = {};
      }
      if (!(indexes instanceof Indexes)) {
        indexes = new Indexes(indexes);
      }
      this.indexes = indexes;
      if (_.isArray(attrs)) {
        data = attrs;
        attrs = null;
      } else {
        options.parse = true;
      }
      this.data = new _DatumArray(data, indexes);
      Series.__super__.constructor.call(this, attrs, options);
    }

    Series.prototype.parse = function(resp, options) {
      this.data.reset(resp.values, options);
      delete resp.values;
      return resp;
    };

    Series.prototype.isColumn = function() {
      return this.width() === 1;
    };

    Series.prototype.isRow = function() {
      return !this.isColumn();
    };

    Series.prototype.size = function() {
      if (this.isColumn()) {
        return this.data.length;
      } else {
        return 1;
      }
    };

    Series.prototype.width = function() {
      return this.indexes.length;
    };

    return Series;

  })(Backbone.Model);
  _SeriesArray = (function(_super) {
    __extends(_SeriesArray, _super);

    function _SeriesArray(attrs, indexes, options) {
      this.model = __bind(this.model, this);
      this.indexes = indexes;
      _SeriesArray.__super__.constructor.call(this, attrs, options);
    }

    _SeriesArray.prototype.model = function(attrs, options) {
      return new Series(attrs, this.indexes, options);
    };

    return _SeriesArray;

  })(Backbone.Collection);
  Frame = (function(_super) {
    __extends(Frame, _super);

    function Frame(attrs, indexes, options) {
      var data;
      if (options == null) {
        options = {};
      }
      if (!(indexes instanceof Indexes)) {
        indexes = new Indexes(indexes);
      }
      this.indexes = indexes;
      if (_.isArray(attrs)) {
        data = attrs;
        attrs = null;
      } else {
        options.parse = true;
      }
      this.series = new _SeriesArray(data, indexes);
      Frame.__super__.constructor.call(this, attrs, options);
    }

    Frame.prototype.parse = function(resp, options) {
      Frame.__super__.parse.call(this, resp, options);
      this.indexes.reset(resp.keys, options);
      this.series.reset(resp.objects, options);
      delete resp.keys;
      delete resp.objects;
      return resp;
    };

    Frame.prototype.size = function() {
      return this.series.length;
    };

    Frame.prototype.width = function() {
      return this.indexes.length;
    };

    Frame.prototype.column = function(index) {
      var data;
      data = this.series.map(function(series) {
        return series.data.at(index);
      });
      return new Series(data, this.indexes.at(index));
    };

    return Frame;

  })(base.Model);
  FrameArray = (function(_super) {
    __extends(FrameArray, _super);

    FrameArray.prototype.model = Frame;

    function FrameArray(attrs, options) {
      this.indexes = new Indexes;
      this.on('reset', function(collection) {
        var model;
        if ((model = collection.models[0])) {
          return this.indexes.reset(model.indexes.models);
        }
      });
      this.on('add', function(model, collection, options) {
        if (collection.length === 1) {
          return this.indexes.reset(model.indexes.models);
        }
      });
      FrameArray.__super__.constructor.call(this, attrs, options);
    }

    return FrameArray;

  })(base.Collection);
  return {
    FrameArray: FrameArray,
    Frame: Frame,
    Series: Series,
    Datum: Datum,
    Index: Index,
    Indexes: Indexes
  };
});
