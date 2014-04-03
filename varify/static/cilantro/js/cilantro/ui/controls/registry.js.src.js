define(['underscore', '../../core', './date', './number', './search', './select', './infograph', './null'], function(_, c, date, number, search, select, infograph, nullSelector) {
  var customControls, defaultControls, get, loadRemote, pendingRemotes, ready, set, _set;
  defaultControls = {
    infograph: infograph.InfographControl,
    number: number.NumberControl,
    date: date.DateControl,
    search: search.SearchControl,
    singleSelectionList: select.SingleSelectionList,
    multiSelectionList: select.MultiSelectionList,
    nullSelector: nullSelector.NullSelector
  };
  customControls = {};
  pendingRemotes = 0;
  loadRemote = function(id, module) {
    pendingRemotes++;
    return require([module], function(func) {
      controlCacheCustom[id] = func;
      return pendingRemotes--;
    }, function(err) {
      return pendingRemotes--;
    });
  };
  _set = function(id, func) {
    switch (typeof func) {
      case 'function':
        return customControls[id] = func;
      case 'string':
        return loadRemote(id, func);
      default:
        throw new Error('control must be a function or AMD module');
    }
  };
  get = function(id) {
    return customControls[id] || defaultControls[id];
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
