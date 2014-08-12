define(["underscore","../core","../constants","../structs","./paginator"],function(e,t,i,n,r){var s=n.Frame.extend({idAttribute:"page_num",url:function(){var i=e.result(this.collection,"url");return t.utils.alterUrlParams(i,{page:this.id,per_page:this.collection.perPage})}}),o=n.FrameArray.extend({initialize:function(){e.bindAll(this,"fetch","markAsDirty","onWorkspaceUnload","onWorkspaceLoad","refresh"),this.isDirty=!0,this.isWorkspaceOpen=!1,this._refresh=e.debounce(this.refresh,i.CLICK_DELAY),t.on(t.VIEW_SYNCED,this.markAsDirty),t.on(t.CONTEXT_SYNCED,this.markAsDirty),this.on("workspace:load",this.onWorkspaceLoad),this.on("workspace:unload",this.onWorkspaceUnload)},onWorkspaceLoad:function(){this.isWorkspaceOpen=!0,this._refresh()},onWorkspaceUnload:function(){this.isWorkspaceOpen=!1},markAsDirty:function(){this.isDirty=!0,this._refresh()},fetch:function(e){e||(e={});var i;if((i=t.config.get("session.defaults.data.preview"))&&(e.type="POST",e.contentType="application/json",e.data=JSON.stringify(i)),this.isDirty&&this.isWorkspaceOpen)return this.isDirty=!1,void 0===e.cache&&(e.cache=!1),n.FrameArray.prototype.fetch.call(this,e);var r=this;return{done:function(){return delete r.pending}}}});return e.extend(o.prototype,r.PaginatorMixin),o.prototype.getPage=function(e,i){if(i||(i={}),this.hasPage(e)){var n=this.get(e);if(!n&&i.load!==!1){n=new this.model({page_num:e}),n.pending=!0,this.add(n);var r,s={};(r=t.config.get("session.defaults.data.preview"))&&(s.type="POST",s.contentType="application/json",s.data=JSON.stringify(r)),n.fetch(s).done(function(){delete n.pending})}return n&&i.active!==!1&&this.setCurrentPage(e),n}},o.prototype.model=s,{Results:o}});
//# sourceMappingURL=results.js.map