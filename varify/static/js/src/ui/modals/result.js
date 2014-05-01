/* global define */

define([
    'jquery',
    'underscore',
    'backbone',
    'marionette',
    '../../utils',
    '../variant'
], function($, _, Backbone, Marionette, utils, variant) {

    /*
        fetchMetricsError: function() {
            $('#assessment-metrics').html('<p class=text-error>Error loading metrics.</p>');
        },

        fetchMetricsSuccess: function() {
            var content, metrics;

            $('#assessment-metrics').html('');

            if (_.isEmpty(this.metrics.get('metrics'))) {
                $('#assessment-metrics').html('<p class=muted>No assessments have been made on this variant</p>');
            }
            else {
                metrics = this.metrics.get('metrics');
                content = [];
                content.push('<div class=row-fluid>');
                content.push('<div class=span4>');
                content.push('<strong>Pathogenicities</strong>' + (Templates.assessmentMetrics(metrics.pathogenicities, true)));
                content.push('</div>');
                content.push('<div class=span4>');
                content.push('<strong>Categories</strong>' + (Templates.assessmentMetrics(metrics.categories, true)));
                content.push('</div>');
                content.push('</div>');
                content.push('<div class=row-fluid>');
                content.push('<table class=assessment-details-table>');
                content.push('<thead><tr><th></th><th>Sample</th><th>User</th><th>Pathogenicity</th><th>Category</th><th>Mother</th><th>Father</th><th>Sanger Requested</th></tr></thead>');
                content.push('<tbody>' + (Templates.assessmentRows(metrics.assessments)) + '</tbody>');
                content.push('</table>');
                content.push('</div>');
                $('#assessment-metrics').append(content.join(' '));
                $('.username-popover').popover();
            }
        },

        renderAssessmentMetricsContainer: function() {
            var content = [];

            content.push('<h4>Assessments</h4>');
            content.push('<div id=assessment-metrics><img src="' + (utils.toAbsolutePath('static/images/loader-tiny.gif')) + '" /></div>');

            return content.join('');
        },

            $row3.append(this._span(this.renderAssessmentMetricsContainer(), 12));

            this.metrics.fetch({
                success: this.fetchMetricsSuccess,
                error: this.fetchMetricsError
            });

            return this.$el;
        }

    });
*/

    var ResultDetails = Marionette.Layout.extend({
        id: 'result-details-modal',

        className: 'modal hide',

        // Fairly arbitray, mostly chosen because it was close to normal height
        // of the sample summary item(1st item in upper left).
        maxExpandableHeight: 300,
        showLessText: 'Show Less...',
        showMoreText: 'Show More...',

        template: 'varify/modals/result',

        selectors: {
            expandableRow: '[data-target=expandable-row]',
            expandableItem: '.expandable-item',
            expandCollapseLink: '[data-target=expand-collapse-link]',
            linkContainer: '.expand-collapse-container'
        },

        ui: {
            // TODO: Can this reference the link selector above?
            expandLinks: '[data-target=expand-collapse-link]'
        },

        regions: {
            summary: '[data-target=summary]',
            effects: '[data-target=effects]',
            phenotypes: '[data-target=phenotypes]',
            scores: '[data-target=prediction-scores]',
            cohorts: '[data-target=cohorts]',
            frequencies: '[data-target=frequencies]',
            articles: '[data-target=articles]',
            clinvar: '[data-target=clinvar]'
        },

        events: {
            'click [data-action=close-result-modal]': 'close',
            'click @ui.expandLinks': 'toggleExpandedState'
        },

        close: function() {
            this.$el.modal('hide');
        },

        onRender: function() {
            this.$el.modal({
                show: false,
                keyboard: false,
                backdrop: 'static'
            });
        },

        /*
         * Reset state of all the expand/collapse links based on whether their
         * item is overflowing. Overflow detection code adapted from Mohsen's
         * answer here:
         *      http://stackoverflow.com/questions/7668636/check-with-jquery-if-div-has-overflowing-elements
         */
        _checkForOverflow: function() {
            _.each($(this.selectors.expandableItem), function(element) {
                var child, hasOverflow = false;

                /*
                 * Note, we purposefully ignore horizontal overflow as it just
                 * isn't relevent here. Note, we use the maxExpandableHeight
                 * here rather than the properties of element to compute
                 * overflow because it is more consistent. element.offsetTop
                 * is measured from the 'content' div while individual children
                 * have their top offset calculated relative to the element
                 * itself so we use maxExpandableHeight to avoid doing any
                 * translations.
                 */
                for (var i = 0; i < element.children.length; i++) {
                    child = element.children[i];

                    if ((child.offsetTop + child.offsetHeight) >
                            this.maxExpandableHeight) {
                        hasOverflow = true;
                        break;
                    }
                }

                // We handle both cases because an item previously might have
                // have been bounded and is now overflown or vice-versa and we
                // want to match the current regardless of previous states.
                if (hasOverflow) {
                    $(element).find(this.selectors.linkContainer).show();
                }
                else {
                    $(element).find(this.selectors.linkContainer).hide();
                }

            }, this);
        },

        // Toggles the expanded/collapsed state of the row containing the item
        // containing the clicked link.
        toggleExpandedState: function(event) {
            var element, parent;

            element = $(event.target);
            parent = element.closest(this.selectors.expandableRow);

            // We essentially link all the expand/collapse links in a single
            // row to take the same action. So, when one is used to expand, all
            // other links in the row get updated in the same fasion to keep
            // them all in sync.
            if (element.text() === this.showMoreText) {
                parent.find(this.selectors.expandCollapseLink)
                      .text(this.showLessText);
                parent.css('height', 'auto')
                      .css('overflow', 'visible');
            }
            else {
                parent.find(this.selectors.expandCollapseLink)
                      .text(this.showMoreText);
                parent.css('height', this.maxExpandableHeight)
                      .css('overflow', 'hidden');
            }
        },

        open: function(result) {
            this.model = result;

            this.summary.show(new variant.Summary({
                model: this.model
            }));

            // We exclude effects that don't have a transcript because the
            // minimum required data we need to display an effect is held
            // within the transcript object.
            this.effects.show(new variant.Effects({
                collection: new Backbone.Collection(utils.groupEffectsByType(
                    _.filter(this.model.get('variant').effects, function(effect) {
                        return effect.transcript !== null;
                    })
                ))
            }));

            this.phenotypes.show(new variant.Phenotypes({
                collection: new Backbone.Collection(
                    utils.groupPhenotypesByType(this.model.get('variant'))
                )
            }));

            this.scores.show(new variant.PredictionScores({
                model: new Backbone.Model(this.model.get('variant'))
            }));

            this.cohorts.show(new variant.Cohorts({
                collection: new Backbone.Collection(
                    this.model.get('variant').cohorts
                )
            }));

            this.frequencies.show(new variant.Frequencies({
                model: new Backbone.Model(this.model.get('variant'))
            }));

            this.articles.show(new variant.Articles({
                collection: new Backbone.Collection(
                    utils.groupArticlesByType(this.model.get('variant'))
                )
            }));

            var clinvarResults;
            if (this.model.get('solvebio') &&
                    this.model.get('solvebio').clinvar) {
                clinvarResults = this.model.get('solvebio').clinvar.results;
            }
            clinvarResults = clinvarResults || [];
            this.clinvar.show(new variant.Clinvar({
                collection: new Backbone.Collection(clinvarResults)
            }));

            this.$el.modal('show');

            // Reset the row and item heights and overflow styles as they may
            // have been toggled previously.
            this.$el.find(this.selectors.expandableRow)
                .css('height', '' + this.maxExpandableHeight + 'px')
                .css('overflow', 'hidden');
            this.$el.find(this.selectors.expandCollapseLink)
                .text(this.showMoreText);

            this._checkForOverflow();
        }

    });

    return {
        ResultDetails: ResultDetails
    };

});
