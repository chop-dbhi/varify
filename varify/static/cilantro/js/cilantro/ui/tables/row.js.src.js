var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', 'marionette', '../base', './cell'], function(_, Marionette, base, cell) {
  var EmptyRow, Row, _ref, _ref1;
  Row = (function(_super) {
    __extends(Row, _super);

    function Row() {
      this.itemViewOptions = __bind(this.itemViewOptions, this);
      _ref = Row.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    Row.prototype.tagName = 'tr';

    Row.prototype.template = function() {};

    Row.prototype.itemView = cell.Cell;

    Row.prototype.itemViewOptions = function(model, index) {
      return _.extend({}, this.options, {
        model: model
      });
    };

    return Row;

  })(Marionette.CollectionView);
  EmptyRow = (function(_super) {
    __extends(EmptyRow, _super);

    function EmptyRow() {
      _ref1 = EmptyRow.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    EmptyRow.prototype.align = 'left';

    EmptyRow.prototype.tagName = 'tr';

    return EmptyRow;

  })(base.LoadView);
  return {
    Row: Row,
    EmptyRow: EmptyRow
  };
});
