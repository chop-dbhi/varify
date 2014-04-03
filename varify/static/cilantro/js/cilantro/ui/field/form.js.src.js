var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

define(['underscore', 'backbone', 'marionette', 'loglevel', '../../core', '../base', './info', './stats', './controls', '../charts'], function(_, Backbone, Marionette, loglevel, c, base, info, stats, controls, charts) {
  var FieldError, FieldForm, FieldFormCollection, FieldLink, FieldLinkCollection, LoadingFields, fieldIdAttr, resolveFieldFormOptions, _ref, _ref1, _ref2, _ref3, _ref4;
  fieldIdAttr = function(concept, field) {
    return "c" + concept + "f" + field;
  };
  resolveFieldFormOptions = function(model) {
    var defaultOptions, formClass, formClassModule, formOptions, instanceOptions, typeOptions;
    formClass = null;
    formClassModule = null;
    formOptions = [{}];
    instanceOptions = c.config.get("fields.instances." + model.id + ".form");
    if (_.isFunction(instanceOptions)) {
      formClass = instanceOptions;
    } else if (_.isString(instanceOptions)) {
      formClassModule = instanceOptions;
    } else if (_.isObject(instanceOptions)) {
      formOptions.push(instanceOptions);
    }
    typeOptions = c.config.get("fields.types." + (model.get('logical_type')) + ".form");
    if (!formClass && _.isFunction(typeOptions)) {
      formClass = typeOptions;
    } else if (!formClassModule && _.isString(typeOptions)) {
      formClassModule = typeOptions;
    } else {
      formOptions.push(typeOptions);
    }
    defaultOptions = c.config.get('fields.defaults.form');
    if (!formClass && _.isFunction(defaultOptions)) {
      formClass = defaultOptions;
    } else if (!formClassModule && _.isString(defaultOptions)) {
      formClassModule = defaultOptions;
    } else {
      formOptions.push(defaultOptions);
    }
    formOptions = _.defaults.apply(null, formOptions);
    return {
      view: formClass,
      module: formClassModule,
      options: formOptions
    };
  };
  LoadingFields = (function(_super) {
    __extends(LoadingFields, _super);

    function LoadingFields() {
      _ref = LoadingFields.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    LoadingFields.prototype.message = 'Loading fields...';

    return LoadingFields;

  })(base.LoadView);
  FieldForm = (function(_super) {
    __extends(FieldForm, _super);

    FieldForm.prototype.className = 'field-form';

    FieldForm.prototype.getTemplate = function() {
      if (this.options.condensed) {
        return 'field/form-condensed';
      } else {
        return 'field/form';
      }
    };

    FieldForm.prototype.options = {
      info: true,
      chart: false,
      stats: true,
      controls: true,
      condensed: false,
      nodeType: 'condition'
    };

    function FieldForm() {
      FieldForm.__super__.constructor.apply(this, arguments);
      this.context = this.options.context.define({
        concept: this.options.context.get('concept'),
        field: this.model.id
      }, {
        type: this.options.nodeType
      });
    }

    FieldForm.prototype.regions = {
      info: '.info-region',
      stats: '.stats-region',
      chart: '.chart-region',
      controls: '.controls-region'
    };

    FieldForm.prototype.regionViews = {
      info: info.FieldInfo,
      stats: stats.FieldStats,
      chart: charts.FieldChart,
      controls: controls.FieldControls
    };

    FieldForm.prototype.onRender = function() {
      var concept;
      concept = this.options.context.get('concept');
      this.$el.attr('id', fieldIdAttr(concept, this.model.id));
      this.renderInfo();
      this.renderStats();
      this.renderControls();
      this.renderChart();
      if (this.options.condensed) {
        return this.$el.addClass('condensed');
      }
    };

    FieldForm.prototype.renderInfo = function() {
      var options;
      if (this.options.info) {
        options = {
          model: this.model
        };
        if (_.isObject(this.options.info)) {
          _.extend(options, this.options.info);
        }
        return this.info.show(new this.regionViews.info(options));
      }
    };

    FieldForm.prototype.renderStats = function() {
      var options;
      if (this.options.stats && (this.model.stats != null)) {
        options = {
          model: this.model
        };
        if (_.isObject(this.options.stats)) {
          _.extend(options, this.options.stats);
        }
        return this.stats.show(new this.regionViews.stats(options));
      }
    };

    FieldForm.prototype.renderControls = function() {
      var attrs, options, _i, _len, _ref1;
      if (this.options.controls) {
        controls = [];
        _ref1 = this.options.controls;
        for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
          options = _ref1[_i];
          attrs = {
            model: this.model,
            context: this.context
          };
          if (_.isObject(options)) {
            _.extend(attrs, options);
          } else {
            attrs.control = options;
          }
          controls.push(attrs);
        }
        return this.controls.show(new this.regionViews.controls({
          collection: new Backbone.Collection(controls)
        }));
      }
    };

    FieldForm.prototype.renderChart = function() {
      var options;
      if (this.options.chart && (this.model.links.distribution != null)) {
        if (this.options.condensed) {
          options = {
            chart: {
              height: 100
            }
          };
        } else {
          options = {
            chart: {
              height: 200
            }
          };
        }
        options.context = this.context;
        options.model = this.model;
        if (_.isObject(this.options.chart)) {
          _.extend(options, this.options.chart);
        }
        return this.chart.show(new this.regionViews.chart(options));
      }
    };

    return FieldForm;

  })(Marionette.Layout);
  FieldError = (function(_super) {
    __extends(FieldError, _super);

    function FieldError() {
      _ref1 = FieldError.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    return FieldError;

  })(base.ErrorView);
  FieldFormCollection = (function(_super) {
    __extends(FieldFormCollection, _super);

    function FieldFormCollection() {
      this.createView = __bind(this.createView, this);
      _ref2 = FieldFormCollection.__super__.constructor.apply(this, arguments);
      return _ref2;
    }

    FieldFormCollection.prototype.itemView = FieldForm;

    FieldFormCollection.prototype.emptyView = LoadingFields;

    FieldFormCollection.prototype.errorView = FieldError;

    FieldFormCollection.prototype.collectionEvents = {
      'reset': 'render'
    };

    FieldFormCollection.prototype.render = function() {
      var _this = this;
      if (this.collection.length) {
        this.collection.each(function(model, index) {
          return _this.renderItem(model, index);
        });
      }
      return this.el;
    };

    FieldFormCollection.prototype.renderItem = function(model, index) {
      var options, result,
        _this = this;
      options = _.extend({}, this.options, {
        model: model,
        context: this.options.context,
        index: index
      });
      if (this.collection.length < 2) {
        options.info = false;
      } else if (index > 0 && this.options.condense) {
        options.condensed = true;
      }
      result = resolveFieldFormOptions(model);
      options = _.extend(options, result.options);
      if (result.module) {
        return require([result.module], function(viewClass) {
          return _this.createView(viewClass, options);
        }, function(err) {
          _this.showErrorView(model);
          return loglevel.debug(err);
        });
      } else {
        return this.createView(result.view || this.itemView, options);
      }
    };

    FieldFormCollection.prototype.createView = function(viewClass, options) {
      var err, view;
      try {
        view = new viewClass(options);
        view.render();
        return c.dom.insertAt(this.$el, options.index, view.el);
      } catch (_error) {
        err = _error;
        this.showErrorView(options.model);
        if (c.config.get('debug')) {
          throw err;
        }
      }
    };

    FieldFormCollection.prototype.showErrorView = function(model) {
      var view;
      view = new this.errorView({
        model: model
      });
      view.render();
      return this.$el.html(view.el);
    };

    return FieldFormCollection;

  })(Marionette.View);
  FieldLink = (function(_super) {
    __extends(FieldLink, _super);

    function FieldLink() {
      _ref3 = FieldLink.__super__.constructor.apply(this, arguments);
      return _ref3;
    }

    FieldLink.prototype.tagName = 'li';

    FieldLink.prototype.template = 'field/link';

    FieldLink.prototype.ui = {
      anchor: 'a'
    };

    FieldLink.prototype.serializeData = function() {
      return {
        name: this.model.get('alt_name') || this.model.get('name')
      };
    };

    return FieldLink;

  })(Marionette.ItemView);
  FieldLinkCollection = (function(_super) {
    __extends(FieldLinkCollection, _super);

    function FieldLinkCollection() {
      _ref4 = FieldLinkCollection.__super__.constructor.apply(this, arguments);
      return _ref4;
    }

    FieldLinkCollection.prototype.template = 'field/links';

    FieldLinkCollection.prototype.itemView = FieldLink;

    FieldLinkCollection.prototype.itemViewContainer = '[data-target=links]';

    FieldLinkCollection.prototype.onAfterItemAdded = function(view) {
      var concept;
      concept = this.options.concept.id;
      return view.ui.anchor.attr('href', '#' + fieldIdAttr(concept, view.model.id));
    };

    return FieldLinkCollection;

  })(Marionette.CompositeView);
  return {
    FieldForm: FieldForm,
    FieldFormCollection: FieldFormCollection,
    FieldLinkCollection: FieldLinkCollection
  };
});
