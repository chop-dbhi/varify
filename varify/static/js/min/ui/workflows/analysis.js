define(["cilantro","marionette","../analysis","../../models"],function(e,t,n,r){var i=t.Layout.extend({className:"analysis-workflow",template:"varify/workflows/analysis",regions:{analyses:".analyses-region",assessments:".assessments-region"},regionViews:{analyses:n.AnalysisList,assessments:n.PathogenictyList},initialize:function(){this.on("router:load",function(){e.panels.context.closePanel({full:!0}),e.panels.concept.closePanel({full:!0})})},onRender:function(){this.analyses.show(new this.regionViews.analyses({collection:new r.AnalysisCollection})),this.assessments.show(new this.regionViews.assessments({collection:new r.PathogenicityCollection}))}});return{AnalysisWorkflow:i}})