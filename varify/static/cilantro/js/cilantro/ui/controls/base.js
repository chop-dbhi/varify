define(["jquery","underscore","backbone","marionette","../../core"],function(t,e,r,i,o){var n=function(){},a={className:"control",attrNames:["concept","field","operator","value"],attrGetters:{concept:"getConcept",field:"getField",operator:"getOperator",value:"getValue"},attrSetters:{concept:"setConcept",field:"setField",operator:"setOperator",value:"setValue"},_get:function(t,e){var r,i;if(r=this.attrGetters[t]){if(i=this[r])return i.call(this,e);throw new Error("Getter declared, but not defined for "+t)}},_set:function(t,e,r){var i,o;if(i=this.attrSetters[t]){if(o=this[i])return o.call(this,e,r);throw new Error("Setter declared, but not defined for "+t)}},wait:function(){if(!this._waiting){this._waiting=!0;var t=this,e=setTimeout(function(){t.trigger("error")},o.config.get("timeouts.control"));this.on("beforeready error",function(){clearTimeout(e)})}},ready:function(t){t&&this._waiting||(delete this._waiting,this.trigger("beforeready"),this.trigger("ready"))},get:function(t,r){if(e.isObject(t)&&(r=t,t=null),t)return this._get(t,r);for(var i,o={},n=0;n<this.attrNames.length;n++)t=this.attrNames[n],void 0!==(i=this._get(t,r))&&(o[t]=i);return o},set:function(t,i,o){var n;e.isObject(t)?(n=t instanceof r.Model?t.toJSON():t,o=i):(n={})[t]=i;for(t in n)void 0!==(i=n[t])&&this._set(t,i,o)},clear:function(t,r){e.isObject(t)&&(r=t,t=null);var i={};if(t)i[t]=void 0;else for(var o=0;o<this.attrNames.length;o++)t=this.attrNames[o],i[t]=void 0;this._set(i,r)},change:function(){this._changing=!0,this.trigger("change",this,this.get()),delete this._changing},validate:function(){},getConcept:n,getField:n,getOperator:n,getValue:n,setConcept:n,setField:n,setOperator:n,setValue:n},s=i.View.extend({}),l=i.ItemView.extend({}),c=i.CollectionView.extend({}),u=i.CompositeView.extend({}),f=i.Layout.extend({});return e.defaults(s.prototype,a),e.defaults(l.prototype,a),e.defaults(c.prototype,a),e.defaults(u.prototype,a),e.defaults(f.prototype,a),{ControlViewMixin:a,ControlView:s,ControlItemView:l,ControlCollectionView:c,ControlCompositeView:u,ControlLayout:f,Control:f}});
//# sourceMappingURL=base.js.map