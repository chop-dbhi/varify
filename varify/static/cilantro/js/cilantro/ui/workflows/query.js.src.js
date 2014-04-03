var __hasProp = {}.hasOwnProperty,
  __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; };

define(['underscore', 'marionette', '../core', '../base', '../concept'], function(_, Marionette, c, base, concept) {
  /*
  The QueryWorkflow provides an interface for navigating and viewing
  concepts that are deemed 'queryable'. This includes browsing the
  available concepts in the index, viewing details about the
  concept in the workspace as well as adding or modifying filters,
  and viewing the list of filters in the context panel.
  
  This view requires the following options:
  - concepts: a collection of concepts that are deemed queryable
  - context: the session/active context model
  */

  var QueryWorkflow, _ref;
  QueryWorkflow = (function(_super) {
    __extends(QueryWorkflow, _super);

    function QueryWorkflow() {
      _ref = QueryWorkflow.__super__.constructor.apply(this, arguments);
      return _ref;
    }

    QueryWorkflow.prototype.className = 'query-workflow';

    QueryWorkflow.prototype.template = 'workflows/query';

    QueryWorkflow.prototype.regions = {
      workspace: '.concept-workspace-region'
    };

    QueryWorkflow.prototype.initialize = function() {
      this.data = {};
      if (!(this.data.context = this.options.context)) {
        throw new Error('context model required');
      }
      if (!(this.data.concepts = this.options.concepts)) {
        throw new Error('concept collection required');
      }
      this.on('router:load', function() {
        c.panels.concept.openPanel();
        return c.panels.context.openPanel();
      });
      return this.on('router:unload', function() {
        return c.panels.concept.closePanel();
      });
    };

    QueryWorkflow.prototype.onRender = function() {
      return this.workspace.show(new concept.ConceptWorkspace({
        context: this.data.context,
        concepts: this.data.concepts
      }));
    };

    return QueryWorkflow;

  })(Marionette.Layout);
  return {
    QueryWorkflow: QueryWorkflow
  };
});
