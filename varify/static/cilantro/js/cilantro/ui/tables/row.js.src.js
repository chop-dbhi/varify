var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', 'marionette', '../base', './cell'], function(_, Marionette, base, cell) {
  var EmptyRow, Row;
  Row = (function(_super) {
    __extends(Row, _super);

    function Row() {
      this.itemViewOptions = __bind(this.itemViewOptions, this);
      return Row.__super__.constructor.apply(this, arguments);
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
      return EmptyRow.__super__.constructor.apply(this, arguments);
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
