var __hasProp={}.hasOwnProperty,__extends=function(t,e){function i(){this.constructor=t}for(var n in e)__hasProp.call(e,n)&&(t[n]=e[n]);return i.prototype=e.prototype,t.prototype=new i,t.__super__=e.prototype,t};define(["backbone"],function(t){var e,i;return e=function(t){function e(){return i=e.__super__.constructor.apply(this,arguments)}return __extends(e,t),e.prototype.tagName="td",e.prototype.initialize=function(){return this.listenTo(this.model.index,"change:visible",this.toggleVisible,this)},e.prototype.render=function(){return this.toggleVisible(),this.$el.html(this.model.get("value")),this},e.prototype.toggleVisible=function(){return this.$el.toggle(this.model.index.get("visible"))},e}(t.View),{Cell:e}});
//@ sourceMappingURL=cell.js.map