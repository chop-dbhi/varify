var __slice = [].slice;

define(['underscore', './tables/cell', './tables/row', './tables/header', './tables/footer', './tables/body', './tables/table'], function() {
  var mods, _;
  _ = arguments[0], mods = 2 <= arguments.length ? __slice.call(arguments, 1) : [];
  return _.extend.apply(_, [{}].concat(__slice.call(mods)));
});
