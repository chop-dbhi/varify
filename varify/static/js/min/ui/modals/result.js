define(["jquery","underscore","backbone","marionette","../result-details"],function(e,t,n,r,i){var s=r.Layout.extend({id:"result-details-modal",className:"modal hide",template:"varify/modals/result",events:{"click [data-action=close-result-modal]":"close"},regions:{details:".variant-details-container"},close:function(){window.SolveBio&&window.SolveBio.Dashboards.delete("variant-detail"),this.$el.modal("hide")},onRender:function(){this.$el.modal({show:!1,keyboard:!1,backdrop:"static"})},open:function(e){this.details.show(new i.ResultDetails({result:e})),this.$el.modal("show"),window.SolveBio&&(window.SolveBio.setApiHost("/"),window.SolveBio.setHeaders({"X-CSRFToken":window.csrf_token}),window.SolveBio.Dashboards.create("variant-detail","/api/solvebio/dashboards/variant-detail","#variant-detail-dashboard").ready(function(n){var r=t.map(e.attributes.variant.effects,function(e){if(e.hgvs_c)return e.transcript.transcript+":"+e.hgvs_c});n.query("ClinVar",{filters:[{or:[["gene_symbols__in",e.attributes.variant.unique_genes],["hgvs__in",[r]],{and:[["chromosome",e.attributes.variant.chr],["position_start__lte",e.attributes.variant.pos],["position_end__gte",e.attributes.variant.pos]]}]}]})}))}});return{ResultDetailsModal:s}})