define(["jquery","underscore","marionette","../../core","../field","../charts","./info"],function(t,e,i,n,o,s,r){var a=i.Layout.extend({className:"concept-form",template:"concept/form",options:{condense:!1,linksMinFields:2},events:{"click .footer [data-toggle=apply]":"applyFilter","click .footer [data-toggle=update]":"applyFilter","click .footer [data-toggle=remove]":"removeFilter","click .footer [data-toggle=revert]":"revertFilter","click [data-target=links] a":"jumpToField"},ui:{state:".footer .state",apply:".footer [data-toggle=apply]",update:".footer [data-toggle=update]",remove:".footer [data-toggle=remove]"},regions:{info:".info-region",links:".links-region",fields:".fields-region"},regionViews:{info:r.ConceptInfo,links:o.FieldLinkCollection,fields:o.FieldFormCollection},contextEvents:{apply:"renderApplied",remove:"renderNew",clear:"renderNew",change:"renderChange",invalid:"renderInvalid"},constructor:function(t){if(t=t||{},this.data={},!(this.data.context=t.context))throw new Error("context model required");if(!t.model)throw new Error("concept model required");this.context=this.data.context.manager.define({concept:t.model.id},{type:"branch"}),i.Layout.prototype.constructor.call(this,t)},delegateEvents:function(){i.Layout.prototype.delegateEvents.apply(this,arguments),this.delegateContextEvents()},undelegateEvents:function(){i.Layout.prototype.undelegateEvents.apply(this,arguments),this.undelegateContextEvents()},delegateContextEvents:function(){var t,e;for(t in this.contextEvents)e=this.contextEvents[t],this.listenTo(this.context,t,this[e])},undelegateContextEvents:function(){var t,e;for(t in this.contextEvents)e=this.contextEvents[t],this.stopListening(this.context,t,this[e])},onRender:function(){var t=new this.regionViews.info({model:this.model}),i=new o.FieldFormCollection(e.defaults({context:this.context,collection:this.model.fields},this.options));this.info.show(t),this.fields.show(i),this.renderChange();var n=this.options.linksMinFields;n!==!1&&(0===this.model.fields.length?this.listenToOnce(this.model.fields,"reset",function(t){t.length>=n&&this._renderLinks()}):this.model.fields.length>this.options.linksMinFields&&this._renderLinks())},_renderLinks:function(){var t=new this.regionViews.links({concept:this.model,collection:this.model.fields});this.links.show(t)},_renderFooter:function(t,e,i){this.ui.state.removeClass("alert-error","alert-warning"),t?this.ui.state.show().html(t):this.ui.state.hide().html(""),e&&this.ui.state.addClass(e),this.ui.apply.prop("disabled",!i),this.ui.update.prop("disabled",!i)},renderChange:function(){this.context.isNew()?this.renderNew():this.renderApplied()},renderInvalid:function(t,e){var i="alert-error",n="<strong>Uh oh.</strong> Cannot apply filter: "+e;this.context.isNew()||(n+=" <a data-toggle=revert class=revert href=#>Revert</a>"),this._renderFooter(n,i,!1)},renderApplied:function(){this.ui.apply.hide(),this.ui.update.show(),this.ui.remove.show();var t,e,i;(t=this.context.isDirty())&&(e="alert-warning",i="<strong>Heads up!</strong> The filter has been changed. <a data-toggle=revert class=revert href=#>Revert</a>"),t=t&&this.context.isValid(),this._renderFooter(i,e,t)},renderNew:function(){this.ui.apply.show(),this.ui.update.hide(),this.ui.remove.hide(),this._renderFooter(null,null,this.context.isValid())},applyFilter:function(t){t&&t.preventDefault(),this.context.apply()},removeFilter:function(t){t&&t.preventDefault(),this.context.remove()},revertFilter:function(t){t&&t.preventDefault(),this.context.revert()},jumpToField:function(e){e.preventDefault();var i=t(e.target.hash).offset().top-20;t("html,body").animate({scrollTop:i})}});return{ConceptForm:a}});
//@ sourceMappingURL=form.js.map