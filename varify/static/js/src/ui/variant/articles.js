/* global define */

define([
    'underscore',
    'cilantro',
    'marionette',
    'backbone'
], function(_, c, Marionette, Backbone) {

    var EmptyArticleView = c.ui.EmptyView.extend({
        className: 'muted',

        icon: '',

        align: 'left'
    });

    var EmptyVariantView = EmptyArticleView.extend({
        message: 'No PubMed articles for this variant'
    });

    var EmptyGeneView = EmptyArticleView.extend({
        message: 'No PubMed articles for this gene'
    });

    var ArticleItem = Marionette.ItemView.extend({
        template: 'varify/variant/article-item',

        tagName: 'li'
    });

    var ArticleGroup = Marionette.CompositeView.extend({
        template: 'varify/variant/article-group',

        tagName: 'ul',

        className: 'unstyled',

        itemView: ArticleItem,

        itemViewContainer: '[data-target=items]',

        getEmptyView: function() {
            if (this.model.get('type') === 'variant') {
                return EmptyVariantView;
            }
            else {
                return EmptyGeneView;
            }
        }
    });

    var Articles = Marionette.CompositeView.extend({
        template: 'varify/variant/articles',

        itemView: ArticleGroup,

        itemViewContainer: '[data-target=items]',

        itemViewOptions: function(model) {
            // Since the articles property is a list of pubmed IDs, we can sort
            // by returning the object itself as it is the pubmed ID we will
            // use when rendering the article.
            return {
                collection: new Backbone.Collection(
                    _.sortBy(model.get('articles'), function(article) {
                        return article;
                    })
                )
            };
        }
    });

    return {
        Articles: Articles
    };

});
