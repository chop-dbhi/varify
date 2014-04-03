var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

define(['underscore', 'backbone', 'marionette', 'loglevel', '../core', '../base', '../welcome', '../field', '../charts', './form', './info'], function(_, Backbone, Marionette, loglevel, c, base, welcome, field, charts, form, info) {
  var ConceptError, ConceptWorkspace, resolveConceptFormOptions, _ref, _ref1;
  resolveConceptFormOptions = function(model) {
    var customForm, defaultOptions, formClass, formClassModule, formOptions, instanceOptions, typeOptions;
    formClass = null;
    formClassModule = null;
    formOptions = [{}];
    instanceOptions = c.config.get("concepts.instances." + model.id + ".form");
    if (_.isFunction(instanceOptions)) {
      formClass = instanceOptions;
    } else if (_.isString(instanceOptions)) {
      formClassModule = instanceOptions;
    } else if (_.isObject(instanceOptions)) {
      formOptions.push(instanceOptions);
    }
    typeOptions = c.config.get("concepts.types." + (model.get('type')) + ".form");
    if (!formClass && _.isFunction(typeOptions)) {
      formClass = typeOptions;
    } else if (!formClassModule && _.isString(typeOptions)) {
      formClassModule = typeOptions;
    } else {
      formOptions.push(typeOptions);
    }
    defaultOptions = c.config.get('concepts.defaults.form');
    if (!formClass && _.isFunction(defaultOptions)) {
      formClass = defaultOptions;
    } else if (!formClassModule && _.isString(defaultOptions)) {
      formClassModule = defaultOptions;
    } else {
      formOptions.push(defaultOptions);
    }
    if (!formClassModule) {
      if ((customForm = c.config.get("concepts.forms." + model.id))) {
        formClassModule = customForm.module;
        formOptions = customForm.options;
        return {
          module: formClassModule,
          options: formOptions
        };
      }
    }
    formOptions = _.defaults.apply(null, formOptions);
    return {
      view: formClass,
      module: formClassModule,
      options: formOptions
    };
  };
  ConceptError = (function(_super) {
    __extends(ConceptError, _super);

    function ConceptError() {
      _ref = ConceptError.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    ConceptError.prototype.template = 'concept/error';

    return ConceptError;

  })(base.ErrorView);
  ConceptWorkspace = (function(_super) {
    __extends(ConceptWorkspace, _super);

    function ConceptWorkspace() {
      this.createView = __bind(this.createView, this);
      this.showItem = __bind(this.showItem, this);
      _ref1 = ConceptWorkspace.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    ConceptWorkspace.prototype.className = 'concept-workspace';

    ConceptWorkspace.prototype.template = 'concept/workspace';

    ConceptWorkspace.prototype.itemView = form.ConceptForm;

    ConceptWorkspace.prototype.errorView = ConceptError;

    ConceptWorkspace.prototype.regions = {
      main: '.main-region'
    };

    ConceptWorkspace.prototype.regionViews = {
      main: welcome.Welcome
    };

    ConceptWorkspace.prototype.initialize = function() {
      this.data = {};
      if (!(this.data.concepts = this.options.concepts)) {
        throw new Error('concept collection required');
      }
      if (!(this.data.context = this.options.context)) {
        throw new Error('context model required');
      }
      return c.on(c.CONCEPT_FOCUS, this.showItem);
    };

    ConceptWorkspace.prototype._ensureModel = function(model) {
      if (!(model instanceof c.models.Concept)) {
        model = this.data.concepts.get(model);
      }
      return model;
    };

    ConceptWorkspace.prototype.showItem = function(model) {
      var options, result,
        _this = this;
      model = this._ensureModel(model);
      if (this.currentView && model.id === this.currentView.model.id) {
        return;
      }
      options = {
        model: model,
        context: this.data.context
      };
      result = resolveConceptFormOptions(model);
      options = _.extend(options, result.options);
      if (result.module) {
        return require([result.module], function(itemView) {
          return _this.createView(itemView, options);
        }, function(err) {
          _this.showErrorView(model);
          return loglevel.debug(err);
        });
      } else {
        return this.createView(result.view || this.itemView, options);
      }
    };

    ConceptWorkspace.prototype.createView = function(itemViewClass, options) {
      var err, view;
      try {
        view = new itemViewClass(options);
        return this.setView(view);
      } catch (_error) {
        err = _error;
        this.showErrorView(options.model);
        if (c.config.get('debug')) {
          throw err;
        }
      }
    };

    ConceptWorkspace.prototype.showErrorView = function(model) {
      var view;
      view = new this.errorView({
        model: model
      });
      this.currentView = view;
      return this.main.show(view);
    };

    ConceptWorkspace.prototype.setView = function(view) {
      this.currentView = view;
      return this.main.show(view);
    };

    ConceptWorkspace.prototype.onRender = function() {
      return this.main.show(new this.regionViews.main);
    };

    return ConceptWorkspace;

  })(Marionette.Layout);
  return {
    ConceptWorkspace: ConceptWorkspace
  };
});
