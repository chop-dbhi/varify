var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', './base', '../button', '../../constants'], function(_, base, button, constants) {
  var RangeControl, _ref;
  RangeControl = (function(_super) {
    __extends(RangeControl, _super);

    function RangeControl() {
      this.readMinMaxStats = __bind(this.readMinMaxStats, this);
      _ref = RangeControl.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    RangeControl.prototype.template = 'controls/range/layout';

    RangeControl.prototype.events = {
      'keyup .range-lower,.range-upper': '_change',
      'change .btn-select': '_change',
      'click .range-help-button': 'toggleHelpText'
    };

    RangeControl.prototype.ui = {
      operatorSelect: '.btn-select',
      lowerBound: '.range-lower',
      upperBound: '.range-upper',
      help: '.help-block'
    };

    RangeControl.prototype.initialize = function(options) {
      this.model.stats.on('reset', this.readMinMaxStats);
      if (this.model.stats.length > 0) {
        this.readMinMaxStats();
      }
      return this._change = _.debounce(this.change, constants.INPUT_DELAY);
    };

    RangeControl.prototype.onRender = function() {
      this.operatorSelect = new button.ButtonSelect({
        collection: [
          {
            value: 'range',
            label: 'between',
            selected: true
          }, {
            value: '-range',
            label: 'not between'
          }
        ]
      });
      this.operatorSelect.render().$el.prependTo(this.$el);
      this.ui.help.hide();
      return this.updateBounds();
    };

    RangeControl.prototype.parseMinStat = function(value) {
      return value;
    };

    RangeControl.prototype.parseMaxStat = function(value) {
      return value;
    };

    RangeControl.prototype.readMinMaxStats = function() {
      var statsMax, statsMin;
      statsMin = this.model.stats.findWhere({
        key: 'min'
      });
      statsMax = this.model.stats.findWhere({
        key: 'max'
      });
      if (statsMin != null) {
        this.minLowerBound = this.parseMinStat(statsMin.get('value'));
      }
      if (statsMax != null) {
        this.maxUpperBound = this.parseMaxStat(statsMax.get('value'));
      }
      return this.updateBounds();
    };

    RangeControl.prototype.toggleHelpText = function(event) {
      this.ui.help.toggle();
      return event.preventDefault();
    };

    RangeControl.prototype.updateBounds = function() {
      if ((this.isClosed != null) && !this.isClosed) {
        if (this.minLowerBound != null) {
          this.setLowerBoundPlaceholder(this.minLowerBound);
        }
        if (this.maxUpperBound != null) {
          return this.setUpperBoundPlaceholder(this.maxUpperBound);
        }
      }
    };

    RangeControl.prototype.getField = function() {
      return this.model.id;
    };

    RangeControl.prototype.getOperator = function() {
      var lower, operator, reverse, upper;
      lower = this.ui.lowerBound.val();
      upper = this.ui.upperBound.val();
      operator = this.operatorSelect.getSelection();
      reverse = operator !== 'range';
      if (lower && upper) {
        operator = operator;
      } else if (lower) {
        operator = reverse ? 'lte' : 'gte';
      } else if (upper) {
        operator = reverse ? 'gte' : 'lte';
      } else {
        operator = null;
      }
      return operator;
    };

    RangeControl.prototype.getLowerBoundValue = function() {
      return this.ui.lowerBound.val();
    };

    RangeControl.prototype.getUpperBoundValue = function() {
      return this.ui.upperBound.val();
    };

    RangeControl.prototype.getValue = function() {
      var lower, upper, value;
      lower = this.getLowerBoundValue();
      upper = this.getUpperBoundValue();
      if ((lower != null) && (upper != null)) {
        value = [lower, upper];
      } else if (lower != null) {
        value = lower;
      } else if (upper != null) {
        value = upper;
      } else {
        value = null;
      }
      return value;
    };

    RangeControl.prototype.setOperator = function(operator) {
      if (operator !== '-range') {
        operator = 'range';
      }
      return this.operatorSelect.setSelection(operator);
    };

    RangeControl.prototype.setLowerBoundPlaceholder = function(value) {
      return this.ui.lowerBound.prop('placeholder', value);
    };

    RangeControl.prototype.setLowerBoundValue = function(value) {
      return this.ui.lowerBound.val(value);
    };

    RangeControl.prototype.setUpperBoundPlaceholder = function(value) {
      return this.ui.upperBound.prop('placeholder', value);
    };

    RangeControl.prototype.setUpperBoundValue = function(value) {
      return this.ui.upperBound.val(value);
    };

    RangeControl.prototype.set = function(attrs) {
      var value;
      this.setOperator(attrs.operator);
      this.setUpperBoundValue();
      this.setLowerBoundValue();
      value = attrs.value;
      if (_.isArray(value)) {
        if (value[0] != null) {
          this.setLowerBoundValue(value[0]);
        }
        if (value[1] != null) {
          return this.setUpperBoundValue(value[1]);
        }
      } else if (value != null) {
        if (attrs.operator === 'gte') {
          return this.setLowerBoundValue(value);
        } else {
          return this.setUpperBoundValue(value);
        }
      }
    };

    return RangeControl;

  })(base.Control);
  return {
    RangeControl: RangeControl
  };
});
