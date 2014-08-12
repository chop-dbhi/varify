var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

define(['jquery', 'underscore', '../base', './core', './utils'], function($, _, base, charts, utils) {
  var ChartLoading, FieldChart;
  ChartLoading = (function(_super) {
    __extends(ChartLoading, _super);

    function ChartLoading() {
      return ChartLoading.__super__.constructor.apply(this, arguments);
    }

    ChartLoading.prototype.message = 'Chart loading...';

    return ChartLoading;

  })(base.LoadView);
  FieldChart = (function(_super) {
    __extends(FieldChart, _super);

    function FieldChart() {
      this.setValue = __bind(this.setValue, this);
      this.chartClick = __bind(this.chartClick, this);
      return FieldChart.__super__.constructor.apply(this, arguments);
    }

    FieldChart.prototype.template = 'charts/chart';

    FieldChart.prototype.loadView = ChartLoading;

    FieldChart.prototype.ui = {
      chart: '.chart',
      heading: '.heading',
      status: '.heading .status'
    };

    FieldChart.prototype.showLoadView = function() {
      var view;
      (view = new this.loadView).render();
      return this.ui.chart.html(view.el);
    };

    FieldChart.prototype.chartClick = function(event) {
      var category, _ref;
      category = (_ref = event.point.category) != null ? _ref : event.point.name;
      event.point.select(!event.point.selected, true);
      return this.change();
    };

    FieldChart.prototype.interactive = function(options) {
      var type, _ref;
      if ((type = (_ref = options.chart) != null ? _ref.type : void 0) === 'pie') {
        return true;
      } else if (type === 'column' && (options.xAxis.categories != null)) {
        return true;
      }
      return false;
    };

    FieldChart.prototype.getChartOptions = function(resp) {
      var options;
      options = utils.processResponse(resp, [this.model]);
      if (options.clustered) {
        this.ui.status.text('Clustered').show();
      } else {
        this.ui.status.hide();
      }
      if (this.interactive(options)) {
        this.setOption('plotOptions.series.events.click', this.chartClick);
      }
      $.extend(true, options, this.chartOptions);
      options.chart.renderTo = this.ui.chart[0];
      return options;
    };

    FieldChart.prototype.getField = function() {
      return this.model.id;
    };

    FieldChart.prototype.getValue = function(options) {
      var point, points;
      points = this.chart.getSelectedPoints();
      return (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = points.length; _i < _len; _i++) {
          point = points[_i];
          _results.push(point.category);
        }
        return _results;
      })();
    };

    FieldChart.prototype.getOperator = function() {
      return 'in';
    };

    FieldChart.prototype.removeChart = function(event) {
      FieldChart.__super__.removeChart.apply(this, arguments);
      if (this.node) {
        return this.node.destroy();
      }
    };

    FieldChart.prototype.onRender = function() {
      if (this.options.parentView != null) {
        this.ui.chart.width(this.options.parentView.$el.width());
      }
      this.showLoadView();
      return this.model.distribution((function(_this) {
        return function(resp) {
          var options;
          if (_this.isClosed) {
            return;
          }
          options = _this.getChartOptions(resp);
          if (resp.size) {
            return _this.renderChart(options);
          } else {
            return _this.showEmptyView(options);
          }
        };
      })(this));
    };

    FieldChart.prototype.setValue = function(value) {
      var point, points, _i, _len, _ref, _ref1;
      if (!_.isArray(value)) {
        value = [];
      }
      if (this.chart != null) {
        points = this.chart.series[0].points;
        for (_i = 0, _len = points.length; _i < _len; _i++) {
          point = points[_i];
          point.select((_ref = point.name) != null ? _ref : (_ref1 = point.category, __indexOf.call(value, _ref1) >= 0), true);
        }
      }
    };

    return FieldChart;

  })(charts.Chart);
  return {
    FieldChart: FieldChart
  };
});
