define(["jquery","underscore","backbone","marionette","../../models","../../utils","../result-details","cilantro"],function(e,t,n,r,i,s,o,u){var a=n.Model.extend({url:function(){var e=s.toAbsolutePath("");return e=e.replace(/variant-sets.*$/g,""),e=e+"api/samples/variants/sets/"+this.id+"/",e}}),f=r.ItemView.extend({className:"variant-item",tagName:"li",template:"varify/workflows/variant-set/empty-variant-item"}),l=r.ItemView.extend({className:"variant-item",tagName:"li",template:"varify/workflows/variant-set/variant-item",modelEvents:{"change:selected":"onSelectedChange"},attributes:function(){return{"data-id":this.model.id}},templateHelpers:{getGeneSymbol:function(){var e="<span class=muted>unknown gene</span>";return this.variant.unique_genes&&this.variant.unique_genes.length&&(e=this.variant.unique_genes[0]),e},getHgvsP:function(){var e="<span class=muted>N/A</span>";if(this.variant.effects&&this.variant.effects.length){var t=this.variant.effects[0];e=t.hgvs_p||t.amino_acid_change||e}return e},getHgvsC:function(){var e="<span class=muted>N/A</span>";return this.variant.effects&&this.variant.effects.length&&(e=this.variant.effects[0].hgvs_c||e),e},getAssessmentCount:function(){return this.num_assessments?""+this.num_assessments+" related assessments":"<span class=muted>This variant has not been assessed</span>"}},onSelectedChange:function(){this.$el.toggleClass("selected",this.model.get("selected"))},serializeData:function(){var e=this.model.toJSON();return e.pchr=u.utils.toDelimitedNumber(e.variant.pos),e}}),c=r.CompositeView.extend({template:"varify/workflows/variant-set/variant-list",itemView:l,itemViewContainer:"[data-target=items]",emptyView:f,events:{"click .variant-item":"onClick"},onClick:function(t){var n=e(t.currentTarget).data("id"),r=this.collection.findWhere({selected:!0});if(r&&r.id===n)return;this.collection.each(function(e){e.id===n?(e.set({selected:!0}),r=e):e.set({selected:!1})}),this.trigger("change:selection",r)}}),h=r.ItemView.extend({template:"varify/workflows/variant-set/knowledge-capture",ui:{form:"form",errorMessage:"[data-target=error-message]",pathogenicity:"[name=pathogenicity-radio]",category:"[name=category-radio]",motherResult:"[data-target=mother-result]",fatherResult:"[data-target=father-result]",evidenceDetails:"[data-target=evidence-details]",sangerRequested:"[name=sanger-radio]",saveButton:"[data-action=save]"},events:{"click @ui.saveButton":"saveAssessment"},initialize:function(){t.bindAll(this,"saveAssessment","onSaveError")},isValid:function(){var e=!0;return this.ui.errorMessage.hide().html(""),t.isEmpty(this.model.get("pathogenicity"))&&(e=!1,this.ui.errorMessage.append("<h5>Please select a pathogenicity.</h5>")),t.isEmpty(this.model.get("assessment_category"))&&(e=!1,this.ui.errorMessage.append("<h5>Please select a category.</h5>")),t.isEmpty(this.model.get("mother_result"))&&(e=!1,this.ui.errorMessage.append("<h5>Please select a result from the &quot;Mother&quot; dropdown.</h5>")),t.isEmpty(this.model.get("father_result"))&&(e=!1,this.ui.errorMessage.append("<h5>Please select a result from the &quot;Father&quot; dropdown.</h5>")),this.model.get("sanger_requested")===undefined&&(e=!1,this.ui.errorMessage.append("<h5>Please select one of the &quot;Sanger Requested&quot; options.</h5>")),e||(this.ui.errorMessage.show(),this.$el.parent().scrollTop(0)),e},onRender:function(){this.model&&this.ui.form.show()},onSaveError:function(){this.ui.errorMessage.show().html("There was an error saving the assessment."),this.$el.parent().scrollTop(0)},onSaveSuccess:function(){u.notify({level:"info",timeout:5e3,dismissable:!0,header:"Assessment Saved!"})},saveAssessment:function(){this.model.set({evidence_details:this.ui.evidenceDetails.val(),sanger_requested:this.ui.sangerRequested.filter(":checked").val(),pathogenicity:this.ui.pathogenicity.filter(":checked").val(),assessment_category:this.ui.category.filter(":checked").val(),mother_result:this.ui.motherResult.val(),father_result:this.ui.fatherResult.val()}),this.isValid()&&this.model.save(null,{success:this.onSaveSuccess,error:this.onSaveError})}}),p=r.Layout.extend({className:"variant-set-workflow row-fluid",template:"varify/workflows/variant-set",ui:{error:"[data-target=error-message]",loading:"[data-target=loading-message]",name:"[data-target=variant-set-name]",count:"[data-target=variant-set-count]",modified:"[data-target=variant-set-modified]",description:"[data-target=variant-set-description]"},regions:{variants:".variant-list-region",variantDetails:".variant-details-region",knowledgeCapture:".knowledge-capture-region"},regionViews:{variants:c,variantDetails:o.ResultDetails,knowledgeCapture:h},initialize:function(){t.bindAll(this,"onChangeSelection","onFetchError","onFetchSuccess"),this.on("router:load",this.onRouterLoad)},onChangeSelection:function(e){var t=new i.Result(e.attributes,{parse:!0}),n=new i.Assessment({sample_result:e.id});e.get("assessment")&&n.set(n.idAttribute,e.get("assessment").id),this.variantDetails.show(new this.regionViews.variantDetails({result:t})),this.knowledgeCapture.show(new this.regionViews.knowledgeCapture({model:n}))},onFetchError:function(){this.ui.loading.hide(),this.showError("There was an error retrieving the variant set from the server. Reload the page to try loading the set again.")},onFetchSuccess:function(e){this.ui.loading.hide(),this.ui.error.hide(),this.ui.name.text(e.get("name")),this.ui.count.text(e.get("count")),this.ui.modified.text(e.get("modified")),this.ui.description.text(e.get("description")),this.variants.currentView.collection.reset(e.get("results")),this.knowledgeCapture.show(new this.regionViews.knowledgeCapture)},onRender:function(){this.variants.show(new this.regionViews.variants({collection:new n.Collection})),this.variants.currentView.on("change:selection",this.onChangeSelection)},onRouterLoad:function(e,t,n){var r=parseInt(n)||null;r?(this.variantSet=new a({id:r}),this.variantSet.fetch({success:this.onFetchSuccess,error:this.onFetchError})):this.showError("There was an issue parsing the variant set ID. Try reloading the page or returning to the Workspace page and clicking on the variant set of interest again.")},showError:function(e){this.ui.error.show().html('<div class="alert alert-error alert-block">'+e+"</div>")}});return{VariantSetWorkflow:p}})