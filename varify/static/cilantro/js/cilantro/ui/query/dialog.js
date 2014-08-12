define(["underscore","marionette","../core"],function(e,i,t){var o=i.ItemView.extend({className:"modal hide",template:"query/delete-dialog",options:{header:"Delete Query"},events:{"click .delete-query-button":"deleteQuery"},ui:{header:".modal-header h4",alert:".alert"},showError:function(e){this.ui.alert.html(e).show()},hideError:function(){this.ui.alert.hide()},deleteQuery:function(){this.hideError();var e=this.model,i=this;this.model.destroy().fail(function(){i.open(e),i.showError("Sorry, there was a problem deleting your query. Please try again.")}),this.close()},onRender:function(){this.ui.header.text(this.options.header),this.$el.modal({show:!1,keyboard:!1,backdrop:"static"})},open:function(e){this.hideError(),this.model=e,this.$el.modal("show")},close:function(){delete this.model,this.$el.modal("hide")}}),r=i.ItemView.extend({className:"modal hide",template:"query/edit-dialog",options:{header:"Query Properties"},events:{"click [data-save]":"saveQuery"},ui:{header:".modal-header h4",alert:".alert",name:".query-name",description:".query-description",email:".query-emails",publicity:".query-publicity"},initialize:function(){if(this.data={},!(this.data.context=this.options.context))throw new Error("context model required");if(!(this.data.view=this.options.view))throw new Error("view model required")},showError:function(e){this.ui.alert.html(e).show()},hideError:function(){this.ui.alert.hide()},saveQuery:function(){if(this.hideError(),!this.ui.name.val())return void this.showError("Please supply a name for the query");var e={name:this.ui.name.val(),description:this.ui.description.val(),usernames_or_emails:this.ui.email.val(),"public":this.ui.publicity.prop("checked")};this.model||(this.model=new this.collection.model,e.context_json=this.data.context.toJSON().json,e.view_json=this.data.view.toJSON().json),this.model.collection||this.collection.add(this.model);var i=this.model,o=this;this.model.save(e).done(function(){t.notify({header:"Saved",level:"info",timeout:5e3,message:"Successfully saved your query"})}).fail(function(){o.open(i),o.showError("Sorry, there was a problem saving your query. Please try again.")}),this.close()},onRender:function(){this.ui.header.text(this.options.header),this.$el.modal({show:!1,keyboard:!1,backdrop:"static"})},open:function(i){this.hideError(),this.model=i;var t,o,r,s;if(i)t=this.model.get("name"),o=this.model.get("description"),r=e.pluck(this.model.get("shared_users"),"email").join(", "),s=this.model.get("public");else{var a=Date().toString().split(" ");t="Query on "+a.slice(0,5).join(" "),o="",r="",s=!1}this.ui.name.val(t),this.ui.description.val(o),this.ui.email.val(r),this.ui.publicity.prop("checked",s),this.$el.modal("show")},close:function(){delete this.model,this.$el.modal("hide")}});return{DeleteQueryDialog:o,EditQueryDialog:r}});
//# sourceMappingURL=dialog.js.map