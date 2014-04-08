var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; },
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  __slice = [].slice;

define(['underscore', 'backbone', 'marionette', './base', '../button'], function(_, Backbone, Marionette, base, button) {
  var Bar, BarChartToolbar, BarCollection, BarModel, Bars, InfographControl, sortModelAttr, _ref, _ref1, _ref2, _ref3, _ref4;
  sortModelAttr = function(attr) {
    return function(model) {
      var value;
      value = model.get(attr);
      if (_.isString(value)) {
        value = value.toLowerCase();
      }
      return value;
    };
  };
  BarModel = (function(_super) {
    __extends(BarModel, _super);

    function BarModel() {
      _ref = BarModel.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    BarModel.prototype.parse = function(attrs) {
      attrs.value = attrs.values[0];
      return attrs;
    };

    return BarModel;

  })(Backbone.Model);
  BarCollection = (function(_super) {
    __extends(BarCollection, _super);

    function BarCollection() {
      _ref1 = BarCollection.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    BarCollection.prototype.model = BarModel;

    BarCollection.prototype.comparator = function(model) {
      return -model.get('count');
    };

    BarCollection.prototype.sortModelsBy = function(attr) {
      var reverse;
      if ((reverse = attr.charAt(0) === '-')) {
        attr = attr.slice(1);
      }
      this.models = this.sortBy(sortModelAttr(attr));
      if (reverse) {
        this.models.reverse();
      }
      this.trigger('sort', this);
    };

    return BarCollection;

  })(Backbone.Collection);
  Bar = (function(_super) {
    __extends(Bar, _super);

    function Bar() {
      _ref2 = Bar.__super__.constructor.apply(this, arguments);
      return _ref2;
    }

    Bar.prototype.className = 'info-bar';

    Bar.prototype.template = 'controls/infograph/bar';

    Bar.prototype.options = {
      total: null
    };

    Bar.prototype.ui = {
      bar: '.bar'
    };

    Bar.prototype.events = {
      'click': 'toggleSelected'
    };

    Bar.prototype.modelEvents = {
      'change:selected': 'setSelected',
      'change:visible': 'setVisible',
      'change:excluded': 'setExcluded'
    };

    Bar.prototype.serializeData = function() {
      var attrs, percentage;
      attrs = this.model.toJSON();
      attrs.value = attrs.values[0];
      percentage = this.getPercentage();
      attrs.width = percentage;
      if (percentage < 1) {
        attrs.percentage = '<1';
      } else {
        attrs.percentage = parseInt(percentage);
      }
      return attrs;
    };

    Bar.prototype.onRender = function() {
      return this.setSelected(this.model, !!this.model.get('selected'));
    };

    Bar.prototype.getPercentage = function() {
      return this.model.get('count') / this.options.total * 100;
    };

    Bar.prototype.toggleSelected = function(event) {
      return this.model.set('selected', !this.model.get('selected'));
    };

    Bar.prototype.setExcluded = function(model, value) {
      return this.$el.toggleClass('excluded', value);
    };

    Bar.prototype.setSelected = function(model, value) {
      this.$el.toggleClass('selected', value);
      if (!value && model.get('visible') === false) {
        return this.$el.removeClass('filtered').hide();
      }
    };

    Bar.prototype.setVisible = function(model, value) {
      if (value) {
        return this.$el.removeClass('filtered').show();
      } else if (model.get('selected')) {
        return this.$el.addClass('filtered');
      } else {
        return this.$el.hide();
      }
    };

    return Bar;

  })(Marionette.ItemView);
  Bars = (function(_super) {
    __extends(Bars, _super);

    function Bars() {
      _ref3 = Bars.__super__.constructor.apply(this, arguments);
      return _ref3;
    }

    Bars.prototype.className = 'info-bar-chart';

    Bars.prototype.itemView = Bar;

    Bars.prototype.itemViewOptions = function(model, index) {
      return {
        model: model,
        total: this.calcTotal()
      };
    };

    Bars.prototype.collectionEvents = {
      'change': 'change',
      'sort': 'sortChildren'
    };

    Bars.prototype.initialize = function() {
      var _this = this;
      this.wait();
      return this.model.distribution(function(resp) {
        _this.collection.reset(resp.data, {
          parse: true
        });
        return _this.ready();
      });
    };

    Bars.prototype.calcTotal = function() {
      var count, total, _i, _len, _ref4;
      total = 0;
      _ref4 = this.collection.pluck('count');
      for (_i = 0, _len = _ref4.length; _i < _len; _i++) {
        count = _ref4[_i];
        total += count;
      }
      return total;
    };

    Bars.prototype.sortChildren = function(collection, options) {
      var _this = this;
      this.collection.each(function(model) {
        var view;
        view = _this.children.findByModel(model);
        return _this.$el.append(view.el);
      });
    };

    Bars.prototype.getField = function() {
      return this.model.id;
    };

    Bars.prototype.getOperator = function() {
      if (this.collection.where({
        excluded: true
      }).length > 0) {
        return '-in';
      } else {
        return 'in';
      }
    };

    Bars.prototype.getValue = function() {
      return _.map(this.collection.where({
        selected: true
      }), function(model) {
        return model.get('value');
      });
    };

    Bars.prototype.setValue = function(values) {
      if (values == null) {
        values = [];
      }
      this.collection.each(function(model) {
        var _ref4;
        return model.set('selected', (_ref4 = model.get('value'), __indexOf.call(values, _ref4) >= 0));
      });
    };

    Bars.prototype.setOperator = function(operator) {
      if (operator === '-in') {
        this.collection.each(function(model) {
          return model.set('excluded', true);
        });
        $('input[name=exclude]').attr('checked', true);
      }
    };

    return Bars;

  })(base.ControlCollectionView);
  BarChartToolbar = (function(_super) {
    __extends(BarChartToolbar, _super);

    function BarChartToolbar() {
      this.toggle = __bind(this.toggle, this);
      _ref4 = BarChartToolbar.__super__.constructor.apply(this, arguments);
      return _ref4;
    }

    BarChartToolbar.prototype.className = 'navbar navbar-toolbar';

    BarChartToolbar.prototype.template = 'controls/infograph/toolbar';

    BarChartToolbar.prototype.events = {
      'keyup [name=filter]': 'filterBars',
      'click [name=invert]': 'invertSelection',
      'click .sort-value-header, .sort-count-header': 'sortBy',
      'change [name=exclude]': 'excludeCheckboxChanged'
    };

    BarChartToolbar.prototype.ui = {
      toolbar: '.btn-toolbar',
      filterInput: '[name=filter]',
      invertButton: '[name=invert]',
      sortValueHeader: '.sort-value-header',
      sortCountHeader: '.sort-count-header',
      excludeCheckbox: '[name=exclude]'
    };

    BarChartToolbar.prototype.initialize = function() {
      return this.sortDirection = '-count';
    };

    BarChartToolbar.prototype.sortBy = function(event) {
      if (event.currentTarget.className === 'sort-value-header') {
        if (this.sortDirection === '-value') {
          this.sortDirection = 'value';
        } else {
          this.sortDirection = '-value';
        }
      } else {
        if (this.sortDirection === '-count') {
          this.sortDirection = 'count';
        } else {
          this.sortDirection = '-count';
        }
      }
      switch (this.sortDirection) {
        case '-count':
          this.ui.sortValueHeader.html('Value <i class=icon-sort></i>');
          this.ui.sortCountHeader.html('Count <i class=icon-sort-down></i>');
          break;
        case 'count':
          this.ui.sortValueHeader.html('Value <i class=icon-sort></i>');
          this.ui.sortCountHeader.html('Count <i class=icon-sort-up></i>');
          break;
        case '-value':
          this.ui.sortValueHeader.html('Value <i class=icon-sort-down></i>');
          this.ui.sortCountHeader.html('Count <i class=icon-sort></i>');
          break;
        case 'value':
          this.ui.sortValueHeader.html('Value <i class=icon-sort-up></i>');
          this.ui.sortCountHeader.html('Count <i class=icon-sort></i>');
      }
      return this.collection.sortModelsBy(this.sortDirection);
    };

    BarChartToolbar.prototype.toggle = function(show) {
      this.ui.filterInput.toggle(show);
      this.ui.invertButton.toggle(show);
      this.ui.sortValueHeader.toggle(show);
      return this.ui.sortCountHeader.toggle(show);
    };

    BarChartToolbar.prototype.filterBars = function(event) {
      var regex, text;
      if (_.isString(event)) {
        text = event;
      } else {
        if (event != null) {
          event.stopPropagation();
        }
        text = this.ui.filterInput.val();
      }
      regex = new RegExp(text, 'i');
      this.collection.each(function(model) {
        return model.set('visible', !text || regex.test(model.get('value')));
      });
    };

    BarChartToolbar.prototype.invertSelection = function(event) {
      this.collection.each(function(model) {
        if (model.get('visible') !== false || model.get('selected')) {
          return model.set('selected', !model.get('selected'));
        }
      });
      this.collection.trigger('change');
    };

    BarChartToolbar.prototype.excludeCheckboxChanged = function() {
      var _this = this;
      this.collection.each(function(model) {
        return model.set('excluded', _this.ui.excludeCheckbox.prop('checked'));
      });
      this.collection.trigger('change');
    };

    return BarChartToolbar;

  })(Marionette.ItemView);
  InfographControl = (function(_super) {
    __extends(InfographControl, _super);

    InfographControl.prototype.template = 'controls/infograph/layout';

    InfographControl.prototype.events = {
      change: 'change'
    };

    InfographControl.prototype.options = {
      minValuesForToolbar: 10
    };

    InfographControl.prototype.regions = {
      bars: '.bars-region',
      toolbar: '.toolbar-region'
    };

    InfographControl.prototype.ui = {
      loading: '[data-target=loading-indicator]'
    };

    InfographControl.prototype.collectionEvents = {
      'reset': 'toggleToolbar'
    };

    function InfographControl(options) {
      this.toggleToolbar = __bind(this.toggleToolbar, this);
      var method, _fn, _i, _len, _ref5,
        _this = this;
      if (options.collection == null) {
        options.collection = new BarCollection;
      }
      InfographControl.__super__.constructor.call(this, options);
      this.barsControl = new Bars({
        model: this.model,
        collection: this.collection
      });
      _ref5 = ['set', 'get', 'when', 'ready', 'wait'];
      _fn = function(method) {
        return _this[method] = function() {
          var args, _ref6;
          args = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
          return (_ref6 = _this.barsControl)[method].apply(_ref6, args);
        };
      };
      for (_i = 0, _len = _ref5.length; _i < _len; _i++) {
        method = _ref5[_i];
        _fn(method);
      }
      this.listenTo(this.barsControl, 'all', function() {
        var args, event;
        event = arguments[0], args = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
        if (event === 'change' || event === 'beforeready' || event === 'ready') {
          this.trigger.apply(this, [event].concat(__slice.call(args)));
        }
        if (event === 'ready') {
          return this.ui.loading.hide();
        }
      });
    }

    InfographControl.prototype.toggleToolbar = function() {
      if (!this.toolbar.currentView) {
        return;
      }
      return this.toolbar.currentView.toggle(this.collection.length >= this.options.minValuesForToolbar);
    };

    InfographControl.prototype.onRender = function() {
      this.bars.show(this.barsControl);
      this.toolbar.show(new BarChartToolbar({
        collection: this.collection
      }));
      return this.toggleToolbar();
    };

    InfographControl.prototype.validate = function(attrs) {
      if (_.isUndefined(attrs.value) || attrs.value.length === 0) {
        return 'Select at least one value';
      }
    };

    return InfographControl;

  })(base.ControlLayout);
  return {
    InfographControl: InfographControl
  };
});
