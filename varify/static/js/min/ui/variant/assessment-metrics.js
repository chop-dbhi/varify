define(["jquery","underscore","backbone","marionette","../../models","../../utils"],function(e,t,n,r,i,s){var o=r.ItemView.extend({tagName:"li",template:"varify/variant/assessment-metrics/user-popover-item"}),u=r.CollectionView.extend({className:"unstyled",tagName:"ul",itemView:o}),a=r.ItemView.extend({tagName:"li",template:"varify/variant/assessment-metrics/percentage-item",ui:{popover:"[data-target=user-popover]"},onRender:function(){var e=new u({collection:new n.Collection(this.model.get("users"))});this.ui.popover.attr("data-content",e.render().el.outerHTML)}}),f=r.CompositeView.extend({template:"varify/variant/assessment-metrics/percentages",itemView:a,itemViewContainer:"[data-target=items]",ui:{popover:"[data-target=user-popover]"},initialize:function(){t.bindAll(this,"hidePopover")},templateHelpers:function(){return{title:this.options.title}},hidePopover:function(e){this.ui.popover.not(e.target).not(e.target.parentElement).popover("hide")},onClose:function(){e(document).off("click",this.hidePopover)},onRender:function(){e(document).on("click",this.hidePopover),this.bindUIElements(),this.ui.popover.popover({container:"#result-details-modal",html:!0,title:"Users who made this call"})}}),l=r.ItemView.extend({tagName:"tr",template:"varify/variant/assessment-metrics/row",ui:{popover:"[data-target=details-popover]"},templateHelpers:function(){var e="samples/"+this.model.get("sample").id;return{sampleUrl:s.toAbsolutePath(e)}},onRender:function(){this.ui.popover.attr("data-content","<p class=details-popover-content>"+this.model.get("details")+"</p>")}}),c=r.CompositeView.extend({template:"varify/variant/assessment-metrics/table",itemView:l,itemViewContainer:"[data-target=items]",ui:{popover:"[data-target=details-popover]"},initialize:function(){t.bindAll(this,"hidePopover")},hidePopover:function(e){this.ui.popover.not(e.target).not(e.target.parentElement).popover("hide")},onClose:function(){e(document).off("click",this.hidePopover)},onRender:function(){e(document).on("click",this.hidePopover),this.bindUIElements(),this.ui.popover.popover({container:"#result-details-modal",placement:"top",html:!0,title:"Evidence Details"})}}),h=r.Layout.extend({template:"varify/variant/assessment-metrics",ui:{empty:"[data-target=empty-message]",error:"[data-target=error-message]",loading:"[data-target=loading-indicator]",metrics:"[data-target=metrics-container]"},regions:{categories:"[data-target=categories]",pathogenicities:"[data-target=pathogenicities]",table:"[data-target=assessment-table]"},modelEvents:{error:"onError",request:"onRequest",sync:"onSync"},initialize:function(){t.bindAll(this,"onError","onRequest","onSync");if(!this.options.variantId)throw new Error("Variant ID Required");this.model=new i.AssessmentMetrics(null,{variantId:this.options.variantId})},onError:function(){this.ui.empty.hide(),this.ui.error.show(),this.ui.loading.hide(),this.ui.metrics.hide()},onRequest:function(){this.ui.empty.hide(),this.ui.error.hide(),this.ui.loading.show(),this.ui.metrics.hide()},onSync:function(){this.ui.empty.hide(),this.ui.error.hide(),this.ui.loading.hide(),this.ui.metrics.hide(),this.model.get("num_assessments")?(this.categories.show(new f({collection:new n.Collection(this.model.get("categories")),title:"Categories"})),this.pathogenicities.show(new f({collection:new n.Collection(this.model.get("pathogenicities")),title:"Pathogenicities"})),this.table.show(new c({collection:new n.Collection(this.model.get("assessments"))})),this.ui.metrics.show()):this.ui.empty.show()},onRender:function(){this.model.fetch()}});return{AssessmentMetrics:h}})