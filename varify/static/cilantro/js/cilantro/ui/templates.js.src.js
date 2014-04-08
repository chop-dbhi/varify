var __slice = [].slice;

define(['tpl!templates/count.html', 'tpl!templates/notification.html', 'tpl!templates/paginator.html', 'tpl!templates/panel.html', 'tpl!templates/search.html', 'tpl!templates/welcome.html', 'tpl!templates/accordian/group.html', 'tpl!templates/accordian/section.html', 'tpl!templates/accordian/item.html', 'tpl!templates/base/error-overlay.html', 'tpl!templates/button/select-option.html', 'tpl!templates/button/select.html', 'tpl!templates/charts/chart.html', 'tpl!templates/charts/editable-chart.html', 'tpl!templates/concept/columns/available-group.html', 'tpl!templates/concept/columns/available-section.html', 'tpl!templates/concept/columns/available-item.html', 'tpl!templates/concept/columns/selected-item.html', 'tpl!templates/concept/columns/layout.html', 'tpl!templates/concept/columns/dialog.html', 'tpl!templates/concept/error.html', 'tpl!templates/concept/form.html', 'tpl!templates/concept/info.html', 'tpl!templates/concept/panel.html', 'tpl!templates/concept/workspace.html', 'tpl!templates/concept/popover.html', 'tpl!templates/export/dialog.html', 'tpl!templates/export/option.html', 'tpl!templates/export/batch.html', 'tpl!templates/export/progress.html', 'tpl!templates/context/panel.html', 'tpl!templates/context/actions.html', 'tpl!templates/context/info.html', 'tpl!templates/context/empty.html', 'tpl!templates/context/filter.html', 'tpl!templates/controls/infograph/bar.html', 'tpl!templates/controls/infograph/layout.html', 'tpl!templates/controls/infograph/toolbar.html', 'tpl!templates/controls/range/layout.html', 'tpl!templates/controls/select/layout.html', 'tpl!templates/controls/select/list.html', 'tpl!templates/controls/search/layout.html', 'tpl!templates/controls/search/item.html', 'tpl!templates/controls/null/layout.html', 'tpl!templates/field/form-condensed.html', 'tpl!templates/field/form.html', 'tpl!templates/field/info.html', 'tpl!templates/field/stats.html', 'tpl!templates/field/links.html', 'tpl!templates/field/link.html', 'tpl!templates/query/delete-dialog.html', 'tpl!templates/query/edit-dialog.html', 'tpl!templates/query/item.html', 'tpl!templates/query/list.html', 'tpl!templates/query/loader.html', 'tpl!templates/values/list.html', 'tpl!templates/workflows/query.html', 'tpl!templates/workflows/results.html', 'tpl!templates/workflows/workspace.html'], function() {
  var customTemplates, defaultTemplates, get, loadRemote, pendingRemotes, ready, set, templateFunc, templateId, templatePathToId, templates, _i, _len, _set;
  templates = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
  defaultTemplates = {};
  customTemplates = {};
  templatePathToId = function(name) {
    return name.replace(/^templates\//, '').replace(/\.html$/, '');
  };
  for (_i = 0, _len = templates.length; _i < _len; _i++) {
    templateFunc = templates[_i];
    templateId = templatePathToId(templateFunc._moduleName);
    templateFunc.templateId = templateId;
    defaultTemplates[templateId] = templateFunc;
  }
  pendingRemotes = 0;
  loadRemote = function(id, module) {
    pendingRemotes++;
    return require([module], function(func) {
      customTemplates[id] = func;
      return pendingRemotes--;
    }, function(err) {
      return pendingRemotes--;
    });
  };
  _set = function(id, func) {
    switch (typeof func) {
      case 'function':
        return customTemplates[id] = func;
      case 'string':
        return loadRemote(id, func);
      default:
        throw new Error('template must be a function or AMD module');
    }
  };
  get = function(id) {
    return customTemplates[id] || defaultTemplates[id];
  };
  set = function(id, func) {
    var key;
    if (typeof id === 'object') {
      for (key in id) {
        func = id[key];
        _set(key, func);
      }
    } else {
      _set(id, func);
    }
  };
  ready = function() {
    return pendingRemotes === 0;
  };
  return {
    get: get,
    set: set,
    ready: ready
  };
});
