define(["underscore","backbone","marionette","../../utils","cilantro/utils/numbers"],function(e,t,n,r,i){var s=t.Model.extend({url:function(){var e=r.toAbsolutePath("");return e=e.replace(/variant-sets.*$/g,""),e=e+"api/samples/variants/sets/"+this.id+"/",e}}),o=n.ItemView.extend({className:"variant-item",tagName:"li",template:"varify/workflows/variant-set/variant-item",events:{click:"onClick"},modelEvents:{"change:selected":"onSelectedChange"},templateHelpers:{getGeneSymbol:function(){var e="<span class=muted>unknown gene</span>";return this.variant.unique_genes&&this.variant.unique_genes.length&&(e=this.variant.unique_genes[0]),e},getHgvsP:function(){var e="<span class=muted>N/A</span>";if(this.variant.effects&&this.variant.effects.length){var t=this.variant.effects[0];e=t.hgvs_p||t.amino_acid_change||e}return e},getHgvsC:function(){var e="<span class=muted>N/A</span>";return this.variant.effects&&this.variant.effects.length&&(e=this.variant.effects[0].hgvs_c||e),e},getAssessmentCount:function(){return this.num_assessments?""+this.num_assessments+" related assessments":"<span class=muted>This variant has not been assessed</span>"}},onClick:function(){this.model.collection.each(function(e){e.set({selected:!1})}),this.model.set({selected:!0})},onSelectedChange:function(){this.$el.toggleClass("selected",this.model.get("selected"))},serializeData:function(){var e=this.model.toJSON();return e.pchr=i.toDelimitedNumber(e.variant.pos),e}}),u=n.CompositeView.extend({template:"varify/workflows/variant-set/variant-list",itemView:o,itemViewContainer:"[data-target=items]"}),a=n.ItemView.extend({template:"varify/workflows/variant-set/variant-details"}),f=n.ItemView.extend({template:"varify/workflows/variant-set/knowledge-capture"}),l=n.Layout.extend({className:"variant-set-workflow row-fluid",template:"varify/workflows/variant-set",ui:{error:"[data-target=error-message]",loading:"[data-target=loading-message]"},regions:{variants:".variant-list-region",variantDetails:".variant-details-region",knowledgeCapture:".knowledge-capture-region"},regionViews:{variants:u,variantDetails:a,knowledgeCapture:f},initialize:function(){e.bindAll(this,"onFetchError","onFetchSuccess"),this.on("router:load",this.onRouterLoad)},onFetchError:function(){this.ui.loading.hide(),this.showError("There was an error retrieving the variant set from the server. Reload the page to try loading the set again.")},onFetchSuccess:function(e){this.ui.loading.hide(),this.ui.error.hide(),this.variants.currentView.collection.reset(e.get("results"))},onRender:function(){this.variants.show(new this.regionViews.variants({collection:new t.Collection})),this.variantDetails.show(new this.regionViews.variantDetails),this.knowledgeCapture.show(new this.regionViews.knowledgeCapture)},onRouterLoad:function(e,t,n){var r=parseInt(n)||null;r?(this.variantSet=new s({id:r}),this.variantSet.fetch({success:this.onFetchSuccess,error:this.onFetchError})):this.showError("There was an issue parsing the variant set ID. Try reloading the page or returning to the Workspace page and clicking on the variant set of interest again.")},showError:function(e){this.ui.error.show().html('<div class="alert alert-error alert-block">'+e+"</div>")}});return{VariantSetWorkflow:l}})