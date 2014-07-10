var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['jquery', 'underscore', 'backbone', 'highcharts', '../base', '../controls', './options'], function($, _, Backbone, Highcharts, base, controls, chartOptions) {
  var AreaChart, AreaSplineChart, BarChart, Chart, ColumnChart, LineChart, OPTIONS_MAP, PieChart, ScatterChart, Sparkline, SplineChart, charts;
  OPTIONS_MAP = {
    el: 'chart.renderTo',
    type: 'chart.type',
    height: 'chart.height',
    width: 'chart.width',
    labelFormatter: 'plotOptions.series.dataLabels.formatter',
    tooltipFormatter: 'tooltip.formatter',
    animate: 'plotOptions.series.animation',
    categories: 'xAxis.categories',
    title: 'title.text',
    subtitle: 'subtitle.text',
    xAxis: 'xAxis.title.text',
    yAxis: 'yAxis.title.text',
    stacking: 'plotOptions.series.stacking',
    legend: 'legend.enabled',
    suffix: 'tooltip.valueSuffix',
    prefix: 'tooltip.valuePrefix',
    series: 'series'
  };
  Chart = (function(_super) {
    __extends(Chart, _super);

    function Chart() {
      return Chart.__super__.constructor.apply(this, arguments);
    }

    Chart.prototype.template = function() {};

    Chart.prototype.emptyView = base.EmptyView;

    Chart.prototype.loadView = base.LoadView;

    Chart.prototype.chartOptions = chartOptions.defaults;

    Chart.prototype.initialize = function(options) {
      var key, value, _base;
      chartOptions = _.extend({}, options.chart);
      if (chartOptions != null) {
        for (key in chartOptions) {
          value = chartOptions[key];
          if (OPTIONS_MAP[key]) {
            this.setOption(OPTIONS_MAP[key], value);
            delete chartOptions[key];
          }
        }
        this.chartOptions = $.extend(true, {}, this.chartOptions, chartOptions);
      }
      Chart.__super__.initialize.call(this, options);
      if ((_base = this.chartOptions).el == null) {
        _base.el = this.el;
      }
    };

    Chart.prototype.setOption = function(key, value) {
      var last, options, tok, toks, _i, _len;
      options = this.chartOptions;
      toks = key.split('.');
      last = toks.pop();
      for (_i = 0, _len = toks.length; _i < _len; _i++) {
        tok = toks[_i];
        if (options[tok] == null) {
          options[tok] = {};
        }
        options = options[tok];
      }
      return options[last] = value;
    };

    Chart.prototype.getChartOptions = function() {
      return this.chartOptions;
    };

    Chart.prototype.showEmptyView = function() {
      var view;
      view = new this.emptyView({
        message: 'No data is available for charting'
      });
      return this.$el.html(view.render().el);
    };

    Chart.prototype.onChartLoaded = function() {
      return $('.load-view').remove();
    };

    Chart.prototype.renderChart = function(options) {
      var view, _base;
      view = new this.loadView({
        message: 'Loading chart'
      });
      this.$el.append(view.render().el);
      options.chart['events'] = {
        load: this.onChartLoaded
      };
      if (this.chart) {
        if (typeof (_base = this.chart).destroy === "function") {
          _base.destroy();
        }
      }
      return this.chart = new Highcharts.Chart(options);
    };

    return Chart;

  })(controls.Control);
  Chart.setDefaultOption = function(key, value) {
    var last, options, prev, prevTok, tok, toks, _i, _len;
    options = this.prototype.chartOptions = _.clone(this.prototype.chartOptions);
    toks = key.split('.');
    last = toks.pop();
    prev = null;
    prevTok = null;
    for (_i = 0, _len = toks.length; _i < _len; _i++) {
      tok = toks[_i];
      prev = options;
      if (prev[tok] != null) {
        options = _.clone(prev[tok]);
      } else {
        options = {};
      }
      prev[tok] = options;
    }
    return options[last] = value;
  };
  AreaChart = (function(_super) {
    __extends(AreaChart, _super);

    function AreaChart() {
      return AreaChart.__super__.constructor.apply(this, arguments);
    }

    return AreaChart;

  })(Chart);
  AreaChart.setDefaultOption('chart.type', 'area');
  AreaSplineChart = (function(_super) {
    __extends(AreaSplineChart, _super);

    function AreaSplineChart() {
      return AreaSplineChart.__super__.constructor.apply(this, arguments);
    }

    return AreaSplineChart;

  })(Chart);
  AreaSplineChart.setDefaultOption('chart.type', 'areaspline');
  BarChart = (function(_super) {
    __extends(BarChart, _super);

    function BarChart() {
      return BarChart.__super__.constructor.apply(this, arguments);
    }

    return BarChart;

  })(Chart);
  BarChart.setDefaultOption('chart.type', 'bar');
  ColumnChart = (function(_super) {
    __extends(ColumnChart, _super);

    function ColumnChart() {
      return ColumnChart.__super__.constructor.apply(this, arguments);
    }

    return ColumnChart;

  })(Chart);
  ColumnChart.setDefaultOption('chart.type', 'column');
  LineChart = (function(_super) {
    __extends(LineChart, _super);

    function LineChart() {
      return LineChart.__super__.constructor.apply(this, arguments);
    }

    return LineChart;

  })(Chart);
  LineChart.setDefaultOption('chart.type', 'line');
  PieChart = (function(_super) {
    __extends(PieChart, _super);

    function PieChart() {
      return PieChart.__super__.constructor.apply(this, arguments);
    }

    return PieChart;

  })(Chart);
  PieChart.setDefaultOption('chart.type', 'pie');
  PieChart.setDefaultOption('legend.enabled', true);
  ScatterChart = (function(_super) {
    __extends(ScatterChart, _super);

    function ScatterChart() {
      return ScatterChart.__super__.constructor.apply(this, arguments);
    }

    return ScatterChart;

  })(Chart);
  ScatterChart.setDefaultOption('chart.type', 'scatter');
  SplineChart = (function(_super) {
    __extends(SplineChart, _super);

    function SplineChart() {
      return SplineChart.__super__.constructor.apply(this, arguments);
    }

    return SplineChart;

  })(Chart);
  SplineChart.setDefaultOption('chart.type', 'spline');
  Sparkline = (function(_super) {
    __extends(Sparkline, _super);

    function Sparkline() {
      return Sparkline.__super__.constructor.apply(this, arguments);
    }

    Sparkline.prototype.chartOptions = chartOptions.sparkline;

    return Sparkline;

  })(Chart);
  charts = {
    Chart: Chart,
    AreaChart: AreaChart,
    AreaSplineChart: AreaSplineChart,
    BarChart: BarChart,
    ColumnChart: ColumnChart,
    LineChart: LineChart,
    PieChart: PieChart,
    ScatterChart: ScatterChart,
    SplineChart: SplineChart,
    Sparkline: Sparkline
  };
  _.extend(Backbone, charts);
  return charts;
});
