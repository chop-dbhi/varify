define(["underscore","./core"],function(t,e){var i=function(i,n){var s,o,r=[{}],a=e.config.get(n+".instances."+i.id+".form");t.isFunction(a)?s=a:t.isString(a)?o=a:t.isObject(a)&&r.push(a);var l=e.config.get(n+".types."+i.get("type")+".form");!s&&t.isFunction(l)?s=l:!o&&t.isString(l)?o=l:r.push(l);var c=e.config.get(n+".defaults.form");return!s&&t.isFunction(c)?s=c:!o&&t.isString(c)?o=c:r.push(c),r=t.defaults.apply(null,r),{view:s,module:o,options:r}};return{resolveFormOptions:i}});
//@ sourceMappingURL=config.js.map