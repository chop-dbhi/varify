define(["jquery"],function(t){function e(e,i,r){r!==!1&&(r=!0),r&&(s=!0),i.done(e.success).fail(e.error).always(e.complete);var a={complete:function(){r&&n()},success:function(){i.resolveWith(this,arguments)},error:function(){i.rejectWith(this,arguments)}},l=o(t.extend({},e,a));i.abort=l.abort}function n(){var t,n,i;(t=r.shift())?(n=t[0],i=t[1],e(n,i)):s=!1}function i(n){var i,o,a;if(i=t.Deferred(),o=(n.type||"get").toLowerCase(),a=null!==n.queue?n.queue:"get"===o?!1:!0,a&&s){var l=[n,i];i.abort=function(){var t=r.indexOf(l);t>-1&&r.splice(t,1),[].unshift.call(arguments,"abort"),i.rejectWith(i,arguments)},r.push(l)}else e(n,i,a);return i}var o=t.ajax,r=[],s=!1;t.ajax=function(t,e){return"string"==typeof t&&(e.url=t,t=e),i(t)},t.hasPendingRequest=function(){return s}});
//@ sourceMappingURL=jquery-ajax-queue.js.map