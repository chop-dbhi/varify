var __bind=function(t,e){return function(){return t.apply(e,arguments)}},__hasProp={}.hasOwnProperty,__extends=function(t,e){function n(){this.constructor=t}for(var r in e)__hasProp.call(e,r)&&(t[r]=e[r]);return n.prototype=e.prototype,t.prototype=new n,t.__super__=e.prototype,t};define(["marionette"],function(t){var e;return e=function(t){function e(){return this.render=__bind(this.render,this),e.__super__.constructor.apply(this,arguments)}return __extends(e,t),e.prototype.tagName="select",e.prototype.options={enumerableOnly:!1},e.prototype.initialize=function(){return this.collection.when(this.render)},e.prototype.render=function(){var t,e,n,r;for(this.$el.append("<option value=>---</option>"),r=this.collection.models,e=0,n=r.length;n>e;e++)t=r[e],t.get("searchable")||(!this.options.enumerableOnly||t.get("enumerable"))&&this.$el.append('<option value="'+t.id+'">'+t.get("name")+"</option>");return this.$el},e.prototype.getSelected=function(){return this.collection.get(parseInt(this.$el.val()))},e}(t.ItemView),{FieldAxis:e}});
//# sourceMappingURL=axis.js.map