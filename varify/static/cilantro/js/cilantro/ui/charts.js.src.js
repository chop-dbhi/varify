var __slice = [].slice;

define(['underscore', './charts/dist', './charts/axis', './charts/editable'], function() {
  var mods, _;
  _ = arguments[0], mods = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
  return _.extend.apply(_, [{}].concat(__slice.call(mods)));
});
