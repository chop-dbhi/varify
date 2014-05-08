var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  __bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

define(['underscore', '../core', '../constants', '../structs', './paginator'], function(_, c, constants, structs, paginator) {
  var Results, ResultsPage, _ref, _ref1;
  ResultsPage = (function(_super) {
    __extends(ResultsPage, _super);

    function ResultsPage() {
      _ref = ResultsPage.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    ResultsPage.prototype.idAttribute = 'page_num';

    ResultsPage.prototype.url = function() {
      var url;
      url = _.result(this.collection, 'url');
      return c.utils.alterUrlParams(url, {
        page: this.id,
        per_page: this.collection.perPage
      });
    };

    return ResultsPage;

  })(structs.Frame);
  Results = (function(_super) {
    __extends(Results, _super);

    function Results() {
      this.fetch = __bind(this.fetch, this);
      this.markAsDirty = __bind(this.markAsDirty, this);
      this.onWorkspaceUnload = __bind(this.onWorkspaceUnload, this);
      this.onWorkspaceLoad = __bind(this.onWorkspaceLoad, this);
      _ref1 = Results.__super__.constructor.apply(this, arguments);
      return _ref1;
    }

    Results.prototype.initialize = function() {
      this.isDirty = true;
      this.isWorkspaceOpen = false;
      this._refresh = _.debounce(_.bind(this.refresh, this), constants.CLICK_DELAY);
      c.on(c.VIEW_SYNCED, this.markAsDirty);
      c.on(c.CONTEXT_SYNCED, this.markAsDirty);
      this.on('workspace:load', this.onWorkspaceLoad);
      return this.on('workspace:unload', this.onWorkspaceUnload);
    };

    Results.prototype.onWorkspaceLoad = function() {
      this.isWorkspaceOpen = true;
      return this._refresh();
    };

    Results.prototype.onWorkspaceUnload = function() {
      return this.isWorkspaceOpen = false;
    };

    Results.prototype.markAsDirty = function() {
      this.isDirty = true;
      return this._refresh();
    };

    Results.prototype.fetch = function(options) {
      var data,
        _this = this;
      if (options == null) {
        options = {};
      }
      if ((data = c.config.get('session.defaults.data.preview')) != null) {
        options.type = 'POST';
        options.contentType = 'application/json';
        options.data = JSON.stringify(data);
      }
      if (this.isDirty && this.isWorkspaceOpen) {
        this.isDirty = false;
        if (options.cache == null) {
          options.cache = false;
        }
        return Results.__super__.fetch.call(this, options);
      } else {
        return {
          done: function() {
            return delete _this.pending;
          }
        };
      }
    };

    return Results;

  })(structs.FrameArray);
  _.extend(Results.prototype, paginator.PaginatorMixin);
  Results.prototype.model = ResultsPage;
  return {
    Results: Results
  };
});
