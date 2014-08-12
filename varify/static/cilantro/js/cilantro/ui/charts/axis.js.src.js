var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['marionette'], function(Marionette) {
  var FieldAxis;
  FieldAxis = (function(_super) {
    __extends(FieldAxis, _super);

    function FieldAxis() {
      this.render = __bind(this.render, this);
      return FieldAxis.__super__.constructor.apply(this, arguments);
    }

    FieldAxis.prototype.tagName = 'select';

    FieldAxis.prototype.options = {
      enumerableOnly: false
    };

    FieldAxis.prototype.initialize = function() {
      return this.collection.when(this.render);
    };

    FieldAxis.prototype.render = function() {
      var model, _i, _len, _ref;
      this.$el.append('<option value=>---</option>');
      _ref = this.collection.models;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        model = _ref[_i];
        if (model.get('searchable')) {
          continue;
        }
        if (this.options.enumerableOnly && !model.get('enumerable')) {
          continue;
        }
        this.$el.append("<option value=\"" + model.id + "\">" + (model.get('name')) + "</option>");
      }
      return this.$el;
    };

    FieldAxis.prototype.getSelected = function() {
      return this.collection.get(parseInt(this.$el.val()));
    };

    return FieldAxis;

  })(Marionette.ItemView);
  return {
    FieldAxis: FieldAxis
  };
});
