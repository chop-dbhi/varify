var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', 'marionette', '../core', '../base', '../query'], function(_, Marionette, c, base, query) {
  var WorkspaceWorkflow, _ref;
  WorkspaceWorkflow = (function(_super) {
    __extends(WorkspaceWorkflow, _super);

    function WorkspaceWorkflow() {
      _ref = WorkspaceWorkflow.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    WorkspaceWorkflow.prototype.className = 'workspace-workflow';

    WorkspaceWorkflow.prototype.template = 'workflows/workspace';

    WorkspaceWorkflow.prototype.regions = {
      queries: '.query-region',
      publicQueries: '.public-query-region',
      editQueryRegion: '.save-query-modal',
      deleteQueryRegion: '.delete-query-modal'
    };

    WorkspaceWorkflow.prototype.regionViews = {
      queries: query.QueryList
    };

    WorkspaceWorkflow.prototype.initialize = function() {
      this.data = {};
      if (c.isSupported('2.2.0') && !(this.data.publicQueries = this.options.public_queries)) {
        throw new Error('public queries collection required');
      }
      if (!(this.data.queries = this.options.queries)) {
        throw new Error('queries collection required');
      }
      if (!(this.data.context = this.options.context)) {
        throw new Error('context model required');
      }
      if (!(this.data.view = this.options.view)) {
        throw new Error('view model required');
      }
      return this.on('router:load', function() {
        c.panels.context.closePanel({
          full: true
        });
        return c.panels.concept.closePanel({
          full: true
        });
      });
    };

    WorkspaceWorkflow.prototype.onRender = function() {
      var publicQueryView, queryView,
        _this = this;
      queryView = new this.regionViews.queries({
        editQueryRegion: this.editQueryRegion,
        deleteQueryRegion: this.deleteQueryRegion,
        collection: this.data.queries,
        context: this.data.context,
        view: this.data.view,
        editable: true
      });
      this.queries.show(queryView);
      if (c.isSupported('2.2.0')) {
        publicQueryView = new this.regionViews.queries({
          collection: this.data.publicQueries,
          context: this.data.context,
          view: this.data.view,
          title: 'Public Queries',
          emptyMessage: "There are no public queries. You can create a new, public query by navigating to the 'Results' page and clicking on the 'Save Query...' button. While filling out the query form, you can mark the query as public which will make it visible to all users and cause it to be listed here."
        });
        this.data.queries.on('sync', function() {
          return _this.data.publicQueries.fetch({
            add: true,
            remove: true,
            merge: true
          });
        });
        return this.publicQueries.show(publicQueryView);
      }
    };

    return WorkspaceWorkflow;

  })(Marionette.Layout);
  return {
    WorkspaceWorkflow: WorkspaceWorkflow
  };
});
