var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['marionette'], function(Marionette) {
  var Cell, _ref;
  Cell = (function(_super) {
    __extends(Cell, _super);

    function Cell() {
      _ref = Cell.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    Cell.prototype.tagName = 'td';

    Cell.prototype.initialize = function() {
      return this.listenTo(this.model.index, 'change:visible', this.toggleVisible, this);
    };

    Cell.prototype.render = function() {
      this.toggleVisible();
      this.$el.html(this.model.get('value'));
      return this;
    };

    Cell.prototype.toggleVisible = function() {
      return this.$el.toggle(this.model.index.get('visible'));
    };

    return Cell;

  })(Marionette.View);
  return {
    Cell: Cell
  };
});
