var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['jquery', 'underscore', './dist', './axis'], function($, _, dist, axis) {
  var EditableFieldChart, _ref;
  EditableFieldChart = (function(_super) {
    __extends(EditableFieldChart, _super);

    function EditableFieldChart() {
      _ref = EditableFieldChart.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    EditableFieldChart.prototype.template = 'charts/editable-chart';

    EditableFieldChart.prototype.events = _.extend({
      'click .fullsize': 'toggleExpanded'
    }, dist.FieldChart.prototype.events);

    EditableFieldChart.prototype.ui = _.extend({
      toolbar: '.btn-toolbar',
      fullsizeToggle: '.fullsize',
      form: '.editable',
      xAxis: '[name=x-Axis]',
      yAxis: '[name=y-Axis]',
      series: '[name=series]'
    }, dist.FieldChart.prototype.ui);

    EditableFieldChart.prototype.onRender = function() {
      var expanded;
      if (this.options.editable === false) {
        this.ui.form.detach();
        return this.ui.toolbar.detach();
      } else {
        this.xAxis = new axis.FieldAxis({
          el: this.ui.xAxis,
          collection: this.collection
        });
        this.yAxis = new axis.FieldAxis({
          el: this.ui.yAxis,
          collection: this.collection
        });
        this.series = new axis.FieldAxis({
          el: this.ui.series,
          enumerableOnly: true,
          collection: this.collection
        });
        if (this.model) {
          if (this.model.get('xAxis')) {
            this.ui.form.hide();
          }
          if ((expanded = this.model.get('expanded'))) {
            return this.expand();
          } else {
            return this.contract();
          }
        }
      }
    };

    EditableFieldChart.prototype.customizeOptions = function(options) {
      var statusText;
      this.ui.status.detach();
      this.ui.heading.text(options.title.text);
      options.title.text = '';
      if (!options.series[0]) {
        this.ui.chart.html('<p class=no-data>Unfortunately, there is\
                    no data to graph here.</p>');
        return;
      }
      this.ui.form.hide();
      statusText = [];
      if (options.clustered) {
        statusText.push('Clustered');
      }
      if (statusText[0]) {
        this.ui.status.text(statusText.join(', ')).show();
        this.ui.heading.append(this.$status);
      }
      if (this.interactive(options)) {
        this.enableChartEvents();
      }
      $.extend(true, options, this.chartOptions);
      options.chart.renderTo = this.ui.chart[0];
      return options;
    };

    EditableFieldChart.prototype.changeChart = function(event) {
      var _this = this;
      if (event) {
        event.preventDefault();
      }
      return this.collection.when(function() {
        var data, fields, series, seriesIdx, url, xAxis, yAxis;
        if (event == null) {
          if ((xAxis = _this.model.get('xAxis'))) {
            _this.xAxis.$el.val(xAxis.toString());
          }
          if ((yAxis = _this.model.get('yAxis'))) {
            _this.yAxis.$el.val(yAxis.toString());
          }
          if ((series = _this.model.get('series'))) {
            _this.series.$el.val(series.toString());
          }
        }
        xAxis = _this.xAxis.getSelected();
        yAxis = _this.yAxis.getSelected();
        series = _this.series.getSelected();
        if (!xAxis) {
          return;
        }
        url = _this.model.get('_links').distribution.href;
        fields = [xAxis];
        data = 'dimension=' + xAxis.id;
        if (yAxis) {
          fields.push(yAxis);
          data = data + '&dimension=' + yAxis.id;
        }
        if (series) {
          seriesIdx = yAxis ? 2 : 1;
          data = data + '&dimension=' + series.id;
        }
        if (event && _this.model) {
          _this.model.set({
            xAxis: xAxis.id,
            yAxis: yAxis ? yAxis.id : void 0,
            series: series ? series.id : void 0
          });
        }
        return _this.update(url, data, fields, seriesIdx);
      });
    };

    EditableFieldChart.prototype.disableSelected = function(event) {
      var $target, value;
      $target = $(event.target);
      if (this.xAxis.el === event.target) {
        this.yAxis.$('option').prop('disabled', false);
        this.series.$('option').prop('disabled', false);
      } else if (this.yAxis.el === event.target) {
        this.xAxis.$('option').prop('disabled', false);
        this.series.$('option').prop('disabled', false);
      } else {
        this.xAxis.$('option').prop('disabled', false);
        this.yAxis.$('option').prop('disabled', false);
      }
      if ((value = $target.val()) !== '') {
        if (this.xAxis.el === event.target) {
          this.yAxis.$("option[value=" + value + "]").prop('disabled', true).val('');
          return this.series.$("option[value=" + value + "]").prop('disabled', true).val('');
        } else if (this.yAxis.el === event.target) {
          this.xAxis.$("option[value=" + value + "]").prop('disabled', true).val('');
          return this.series.$("option[value=" + value + "]").prop('disabled', true).val('');
        } else {
          this.xAxis.$("option[value=" + value + "]").prop('disabled', true).val('');
          return this.yAxis.$("option[value=" + value + "]").prop('disabled', true).val('');
        }
      }
    };

    EditableFieldChart.prototype.toggleExpanded = function(event) {
      var expanded;
      expanded = this.model.get('expanded');
      if (expanded) {
        this.contract();
      } else {
        this.expand();
      }
      return this.model.save({
        expanded: !expanded
      });
    };

    EditableFieldChart.prototype.resize = function() {
      var chartWidth;
      chartWidth = this.ui.chart.width();
      if (this.chart) {
        return this.chart.setSize(chartWidth, null, false);
      }
    };

    EditableFieldChart.prototype.expand = function() {
      this.$fullsizeToggle.children('i').removeClass('icon-resize-small').addClass('icon-resize-full');
      this.$el.addClass('expanded');
      return this.resize();
    };

    EditableFieldChart.prototype.contract = function() {
      this.$fullsizeToggle.children('i').removeClass('icon-resize-full').addClass('icon-resize-small');
      this.$el.removeClass('expanded');
      return this.resize();
    };

    EditableFieldChart.prototype.hideToolbar = function() {
      return this.ui.toolbar.fadeOut(200);
    };

    EditableFieldChart.prototype.showToolbar = function() {
      return this.ui.toolbar.fadeIn(200);
    };

    EditableFieldChart.prototype.toggleEdit = function(event) {
      if (this.ui.form.is(':visible')) {
        return this.ui.form.fadeOut(300);
      } else {
        return this.ui.form.fadeIn(300);
      }
    };

    return EditableFieldChart;

  })(dist.FieldChart);
  return {
    EditableFieldChart: EditableFieldChart
  };
});
