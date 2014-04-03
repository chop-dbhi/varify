var __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['jquery', 'underscore', 'backbone', 'marionette', '../core', '../base', '../charts', '../charts/utils'], function($, _, Backbone, Marionette, c, base, charts, utils) {
  var FieldStatValue, FieldStats, FieldStatsChart, FieldStatsValues, prettyValue, _ref, _ref1, _ref2, _ref3;
  prettyValue = function(value) {
    if (_.isNumber(value)) {
      return c.utils.prettyNumber(value);
    } else {
      return value;
    }
  };
  FieldStatValue = (function(_super) {
    __extends(FieldStatValue, _super);

    function FieldStatValue() {
      this.template = __bind(this.template, this);
      _ref = FieldStatValue.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    FieldStatValue.prototype.tagName = 'li';

    FieldStatValue.prototype.keyMap = {
      min: 'Min',
      max: 'Max',
      avg: 'Average',
      count: 'Count',
      distinct_count: 'Unique values'
    };

    FieldStatValue.prototype.template = function(data) {
      return "<span class=stat-label>" + (this.keyMap[data.key] || data.key) + "</span>                <span class=stat-value title=\"" + data.value + "\">" + (prettyValue(data.value)) + "</span>";
    };

    return FieldStatValue;

  })(Marionette.ItemView);
  FieldStatsValues = (function(_super) {
    __extends(FieldStatsValues, _super);

    function FieldStatsValues() {
      _ref1 = FieldStatsValues.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    FieldStatsValues.prototype.tagName = 'ul';

    FieldStatsValues.prototype.itemView = FieldStatValue;

    return FieldStatsValues;

  })(Marionette.CollectionView);
  FieldStatsChart = (function(_super) {
    __extends(FieldStatsChart, _super);

    function FieldStatsChart() {
      _ref2 = FieldStatsChart.__super__.constructor.apply(this, arguments);
      return _ref2;
    }

    FieldStatsChart.prototype.className = 'sparkline';

    FieldStatsChart.prototype.chartOptions = Backbone.Sparkline.prototype.chartOptions;

    FieldStatsChart.prototype.getChartOptions = function(resp) {
      var options;
      options = {
        series: [utils.getSeries(resp.data)]
      };
      $.extend(true, options, this.chartOptions);
      options.chart.renderTo = this.ui.chart[0];
      return options;
    };

    return FieldStatsChart;

  })(charts.FieldChart);
  FieldStats = (function(_super) {
    __extends(FieldStats, _super);

    function FieldStats() {
      _ref3 = FieldStats.__super__.constructor.apply(this, arguments);
      return _ref3;
    }

    FieldStats.prototype.className = 'field-stats';

    FieldStats.prototype.template = 'field/stats';

    FieldStats.prototype.regions = {
      values: '.stats-values',
      chart: '.stats-chart'
    };

    FieldStats.prototype.onRender = function() {
      if (this.model.stats != null) {
        this.values.show(new FieldStatsValues({
          collection: this.model.stats
        }));
        if (!this.model.stats.length) {
          return this.model.stats.fetch({
            reset: true
          });
        }
      }
    };

    return FieldStats;

  })(Marionette.Layout);
  return {
    FieldStats: FieldStats
  };
});
