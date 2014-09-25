/* global define */

define([
    'jquery',
    'underscore',
    'marionette',
    '../lib/solvebio',
    '../models',
    './variant'
], function($, _, Marionette, SolveBio, models, details) {

    var createSolveBioDashboard = function(attrs) {
        // Delete and recreate the dashboard if found
        // TODO: destroy the dashboard on view change
        if (SolveBio.Dashboards.get('variantDetailDashboard')) {
            SolveBio.Dashboards.delete('variantDetailDashboard');
        }
        SolveBio.Dashboards.create(
            'variantDetailDashboard',
            '/api/solvebio/dashboards/variant-detail',
            '#solvebio-variant-detail'
        ).ready(function(dash) {
            // Filter by position +- 1000, rsid, and hgvs values
            var filters = [{
                and: [['hg18_chromosome', attrs.variant.chr],
                      ['hg18_start__range', [attrs.variant.pos - 1000,
                                             attrs.variant.pos + 1000]]]
            }];

            if (attrs.variant.rsid) {
                filters.push(['rsid', attrs.variant.rsid]);
            }

            var hgvs = [];
            /* jshint ignore:start */
            _.each(attrs.variant.effects, function(effect) {
                if (effect.hgvs_c && effect.transcript.transcript) {
                    hgvs.push(effect.transcript.transcript + ':' + effect.hgvs_c);
                }
            });

            if (hgvs.length > 0) {
                filters.push(['hgvs__in', hgvs]);
            }
            /* jshint ignore:end */

            dash.postMessage({
                header: {
                    'id': '[#' + attrs.sample.id + ']',
                    'subtitle': 'in ' + attrs.sample.project,
                    'title': attrs.sample.label,
                    'alt': attrs.variant.alt,
                    'ref': attrs.variant.ref,
                    'quality': attrs.quality,
                    'read_depth': attrs.raw_read_depth, // jshint ignore:line
                    'hgvs': hgvs,
                    'chr': attrs.variant.chr,
                    'pos': attrs.variant.pos
                },
                clinvar: {
                    filters: [{'or': filters}]
                }
            });
        });
    };

    var ResultDetails = Marionette.Layout.extend({
        className: 'result-details',

        template: 'varify/result-details',

        // Fairly arbitray, mostly chosen because it was close to normal height
        // of the sample summary item(1st item in upper left).
        maxExpandableHeight: 360,
        showLessText: 'Show Less...',
        showMoreText: 'Show More...',

        ui: {
            expandableRows: '[data-target=expandable-row]',
            expandableItems: '.expandable-item',
            expandCollapseLinks: '[data-target=expand-collapse-link]',
            linkContainers: '.expand-collapse-container'
        },

        regions: {
            summary: '[data-target=summary]',
            effects: '[data-target=effects]',
            phenotypes: '[data-target=phenotypes]',
            scores: '[data-target=prediction-scores]',
            cohorts: '[data-target=cohorts]',
            frequencies: '[data-target=frequencies]',
            articles: '[data-target=articles]',
            assessmentMetrics: '[data-target=assessment-metrics]'
        },

        events: {
            'click @ui.expandCollapseLinks': 'toggleExpandedState'
        },

        initialize: function() {
            if (!(this.model = this.options.result)) {
                throw new Error('A valid result object must be supplied');
            }
        },

        /* jshint ignore:start */

        /*
         *
         * Reset state of all the expand/collapse links based on whether their
         * item is overflowing. Overflow detection code adapted from Mohsen's
         * answer here:
         *      http://stackoverflow.com/questions/7668636/check-with-jquery-if-div-has-overflowing-elements
         *
         */

        /* jshint ignore:end */
        _checkForOverflow: function() {
            _.each(this.ui.expandableItems, function(element) {
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
                    $(element).find(this.ui.linkContainers).show();
                }
                else {
                    $(element).find(this.ui.linkContainers).hide();
                }

            }, this);
        },

        // Toggles the expanded/collapsed state of the row containing the item
        // containing the clicked link.
        toggleExpandedState: function(event) {
            var element, parent;

            element = $(event.target);
            parent = element.closest(this.ui.expandableRows);

            // We essentially link all the expand/collapse links in a single
            // row to take the same action. So, when one is used to expand, all
            // other links in the row get updated in the same fasion to keep
            // them all in sync.
            if (element.text() === this.showMoreText) {
                parent.find(this.ui.expandCollapseLinks)
                      .text(this.showLessText);
                parent.css({height: 'auto', overflow: 'visible'});
            }
            else {
                parent.find(this.ui.expandCollapseLinks)
                      .text(this.showMoreText);
                parent.css({
                    height: this.maxExpandableHeight,
                    overflow: 'hidden'
                });
            }
        },

        onDomRefresh: function() {
            // By executing this check here, we are guaranteed to have the
            // offsetTop and offsetHeight properties necessary for detecting
            // overflow. Executing this in onRender resulted in those offset*
            // properties always having values of 0 making it impossible to
            // detect overflow anywhere but here.
            this._checkForOverflow();

            // Set up the SolveBio dashboard
            var dashboardAttrs = this.model.attributes;
            if (SolveBio.getAccessToken()) {
                createSolveBioDashboard(dashboardAttrs);
            } else if (!SolveBio.disabled) {
                // Get SolveBio access token
                $.getJSON('/api/solvebio/oauth2/token', function(data) {
                    if (data.access_token) {  // jshint ignore:line
                        SolveBio.setAccessToken(data.access_token);  // jshint ignore:line
                        createSolveBioDashboard(dashboardAttrs);
                    } else {
                        // No access token, disable so we never try again
                        SolveBio.disabled = true;
                    }
                });
            }
        },

        onRender: function() {
            var variant = new models.Variant(this.model.get('variant'));

            this.summary.show(new details.Summary({
                model: this.model
            }));

            // We exclude effects that don't have a transcript because the
            // minimum required data we need to display an effect is held
            // within the transcript object.
            this.effects.show(new details.Effects({
                collection: variant.effects
            }));

            this.phenotypes.show(new details.Phenotypes({
                collection: variant.phenotypes
            }));

            this.scores.show(new details.PredictionScores({
                model: variant
            }));

            this.cohorts.show(new details.Cohorts({
                collection: variant.cohorts
            }));

            this.frequencies.show(new details.Frequencies({
                model: variant
            }));

            this.articles.show(new details.Articles({
                collection: variant.articles
            }));

            this.assessmentMetrics.show(new details.AssessmentMetrics({
                variantId: variant.id,
            }));

            // Since the UI elements are bound before rendering, many of the
            // UI elements we need access to to will not be found at this point
            // as they did not exist in the templates and therefore would not
            // be found during the normal UI binding call. We rebind here so
            // since all the elements should now be available as all the
            // regions have been populated and their views shown.
            this.bindUIElements();

            // Reset the row and item heights and overflow styles as they may
            // have been toggled previously.
            this.ui.expandableRows
                .css('height', '' + this.maxExpandableHeight + 'px')
                .css('overflow', 'hidden');

            this.ui.expandCollapseLinks.text(this.showMoreText);
        }
    });

    return {
        ResultDetails: ResultDetails
    };

});
