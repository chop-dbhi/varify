define(["jquery","underscore","backbone","./models","./utils","./router","./core"],function(t,e,i,n,s,o,r){var a={SESSION_OPENING:"session:opening",SESSION_ERROR:"session:error",SESSION_UNAUTHORIZED:"session:unauthorized",SESSION_OPENED:"session:opened",SESSION_CLOSED:"session:closed"},h={concepts:n.Concepts,fields:n.FieldCollection,contexts:n.ContextCollection,views:n.ViewCollection,preview:n.Results,exporter:n.ExporterCollection,queries:n.Queries,public_queries:n.Queries,stats:n.Stats},u=n.Model.extend({idAttribute:"url",options:function(){return r.config.get("session.defaults")},initialize:function(t,i){this.options=e.extend({},e.result(this,"options"),i),this.opened=!1,this.started=!1,this.opening=!1,this.state={},e.bindAll(this,"ping","startPing","stopPing")},validate:function(t){return t&&t.url?void 0:"url is required"},startPing:function(){this.links.ping&&this.options.ping&&!this._ping&&(this.ping(),this._ping=setInterval(this.ping,this.options.ping))},stopPing:function(){clearTimeout(this._ping),delete this._ping},ping:function(){var t=this;i.ajax({type:"GET",url:this.links.ping,dataType:"json",success:function(e){"timeout"===e.status&&(t.stopPing(),t.timeout(e.location))},error:function(e,i,n){t.stopPing(),"FOUND"===n&&this.timeout(e.getResponseHeader("Location"))}})},timeout:function(t){var e;e=t?'Your session timed out. Please <a href="'+t+'">refresh the page</a>.':"Your session timed out. Please refresh the page.",r.notify({header:"Session Timeout",message:e,dismissable:!1,timeout:!1,level:"warning"}),setTimeout(function(){t?window.location=location:window.location.reload(!0)},5e3)},parse:function(t){t=t||{},this.title=t.title,this.version=t.version,this.data={};var i;e.each(t._links,function(t,e){(i=h[e])&&(this.data[e]=new i,this.data[e].url=t.href,this.data[e].fetch({reset:!0}))},this),this.router=new o.Router({main:r.config.get("main"),root:r.config.get("root")});var n=this.get("routes");if(n)if("string"==typeof n){var s=this;require([n],function(t){s.router.register(t)})}else"function"==typeof n&&(n=n()),this.router.register(n);return t},open:function(){if(this.opened||this.opening)return this._opening.promise();if(!this.isValid())throw new Error(this.validationError);this.opening=!0,this._opening=t.Deferred();var e={url:this.get("url"),type:"GET",dataType:"json"},i=this.get("credentials");i&&t.extend(e,{type:"POST",contentType:"application/json",data:JSON.stringify(i)});var n=this;return this.fetch(e).always(function(){n.opening=!1}).done(function(t,e,i){n.opened=!0,n._opening.resolveWith(n,[n,t,e,i])}).fail(function(t,e,i){n.error=i,n._opening.rejectWith(n,[this,t,e,i])}),this._opening.promise()},close:function(){this.end(),this.opening=this.opened=!1,e.each(this.data,function(t){t.reset?t.reset():t.clear(),delete t.url}),delete this._opening,delete this.data},start:function(t,e){if(this.started)return!1;if(!this.opened)throw new Error("Session must be opened before loaded");this.started=!0,t&&this.router.register(t),this.router.start(e),this.startPing(),this.listenTo(r,{visible:this.startPing,hidden:this.stopPing,focus:this.startPing,blur:this.stopPing}),r.isSupported(r.getSerranoVersion())||r.notify({header:"Serrano Version Unsupported",level:"warning",timeout:!1,message:"You are connecting to an unsupported version of Serrano. Some functionality may be broken or missing due to compatibility issues."})},end:function(){this.started=!1,this.stopPing(),this.stopListening(r,"visible hidden"),this.router.unregister()}}),l=i.Collection.extend({_switch:function(t){this.active!==t&&(delete this.pending,this.close(),this.active=t,this.trigger(a.SESSION_OPENED,t))},open:function(t,e){"object"==typeof t?e=t:(e=e||{},e.url=t);var i=this.get(e.url);i||(i=new u(e),this.add(i)),i!==this.active&&i!==this.pending&&(this.pending=i,this.trigger(a.SESSION_OPENING,i));var n=this;return i.open().done(function(){n.pending===i&&n._switch(i)}).fail(function(t,e,s,o){if(n.pending===i){n.pending=null;var r;r=401===e.statusCode||403===e.statusCode?a.SESSION_UNAUTHORIZED:a.SESSION_ERROR,n.trigger(r,i,o)}})},close:function(){if(this.active){var t=this.active;delete this.active,this.remove(t),t.close(),this.trigger(a.SESSION_CLOSED,t)}},clear:function(){this.close(),this.reset()}});return e.extend({SessionManager:l,Session:u,events:a})});
//# sourceMappingURL=session.js.map