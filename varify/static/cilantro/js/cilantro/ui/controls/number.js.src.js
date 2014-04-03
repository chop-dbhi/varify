var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['./range'], function(range) {
  var NumberControl, _ref;
  NumberControl = (function(_super) {
    __extends(NumberControl, _super);

    function NumberControl() {
      _ref = NumberControl.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    NumberControl.prototype.getLowerBoundValue = function() {
      var value;
      if ((value = this.ui.lowerBound.val().trim())) {
        return parseFloat(value);
      }
    };

    NumberControl.prototype.getUpperBoundValue = function() {
      var value;
      if ((value = this.ui.upperBound.val().trim())) {
        return parseFloat(value);
      }
    };

    return NumberControl;

  })(range.RangeControl);
  return {
    NumberControl: NumberControl
  };
});
