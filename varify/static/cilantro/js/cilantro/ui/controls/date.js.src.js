var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', './range'], function(_, range) {
  var DateControl, _ref;
  DateControl = (function(_super) {
    __extends(DateControl, _super);

    function DateControl() {
      _ref = DateControl.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    DateControl.prototype._events = {
      'changeDate .range-lower,.range-upper': '_change'
    };

    DateControl.prototype.initialize = function() {
      DateControl.__super__.initialize.apply(this, arguments);
      return this.events = _.extend({}, this._events, this.events);
    };

    DateControl.prototype.onRender = function() {
      DateControl.__super__.onRender.apply(this, arguments);
      this.ui.lowerBound.datepicker({
        'autoclose': true
      });
      return this.ui.upperBound.datepicker({
        'autoclose': true
      });
    };

    DateControl.prototype.getLowerBoundValue = function() {
      return this.ui.lowerBound.datepicker('getFormattedDate');
    };

    DateControl.prototype.getUpperBoundValue = function() {
      return this.ui.upperBound.datepicker('getFormattedDate');
    };

    DateControl.prototype._parseDate = function(value) {
      if (value != null) {
        return value.replace(/-/g, '/');
      }
    };

    DateControl.prototype.parseMinStat = function(value) {
      return this._parseDate(value);
    };

    DateControl.prototype.parseMaxStat = function(value) {
      return this._parseDate(value);
    };

    DateControl.prototype._setPlaceholder = function(element, value) {
      var date, dateStr;
      date = new Date(value);
      dateStr = "" + (date.getMonth() + 1) + "/" + (date.getDate()) + "/" + (date.getFullYear());
      return element.attr('placeholder', dateStr);
    };

    DateControl.prototype.setLowerBoundPlaceholder = function(value) {
      return this._setPlaceholder(this.ui.lowerBound, value);
    };

    DateControl.prototype.setUpperBoundPlaceholder = function(value) {
      return this._setPlaceholder(this.ui.upperBound, value);
    };

    DateControl.prototype._setValue = function(element, value) {
      var dateString;
      dateString = value != null ? value.val() : void 0;
      if ((dateString != null) && dateString !== "") {
        return element.datepicker('setDate', new Date(dateString));
      } else {
        return element.datepicker('_clearDate', this);
      }
    };

    DateControl.prototype.setLowerBoundValue = function(value) {
      return this._setValue(this.ui.lowerBound, value);
    };

    DateControl.prototype.setUpperBoundValue = function(value) {
      return this._setValue(this.ui.upperBound, value);
    };

    return DateControl;

  })(range.RangeControl);
  return {
    DateControl: DateControl
  };
});
