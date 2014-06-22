/* global define */

define([
    'jquery',
    'underscore',
    'backbone',
    'marionette',
    '../result-details'
], function($, _, Backbone, Marionette, details) {

    var ResultDetailsModal = Marionette.Layout.extend({
        id: 'result-details-modal',

        className: 'modal hide',

        template: 'varify/modals/result',

        events: {
            'click [data-action=close-result-modal]': 'close'
        },

        regions: {
            details: '.variant-details-container'
        },

        close: function() {
            if (window.SolveBio) {
                window.SolveBio.Dashboards.delete('variant-detail');
            }
            this.$el.modal('hide');
        },

        onRender: function() {
            this.$el.modal({
                show: false,
                keyboard: false,
                backdrop: 'static'
            });
        },

        open: function(result) {
            this.details.show(new details.ResultDetails({
                result: result
            }));

            this.$el.modal('show');

            if (window.SolveBio) {
                window.SolveBio.setApiHost('/');
                window.SolveBio.setHeaders({
                    'X-CSRFToken': window.csrf_token // jshint ignore:line
                });
                window.SolveBio.Dashboards.create(
                    'variant-detail',
                    '/api/solvebio/dashboards/variant-detail',
                    '#variant-detail-dashboard'
                ).ready(function(dash) {
                    // assemble HGVS values
                    // TODO: do this in variant resource?
                    var hgvsC = _.map(result.attributes.variant.effects,
                        function(effect) {
                            if (effect.hgvs_c) { // jshint ignore:line
                                return effect.transcript.transcript + ':' + effect.hgvs_c; // jshint ignore:line
                            }
                        }
                    );

                    // TODO: use SolveBio chainable query builder
                    dash.query(
                        'ClinVar',
                        {
                            filters: [{
                                'or': [
                                        ['gene_symbols__in', result.attributes.variant.unique_genes], // jshint ignore:line
                                        ['hgvs__in', [hgvsC]],
                                        {
                                            'and': [
                                                ['chromosome', result.attributes.variant.chr], // jshint ignore:line
                                                ['position_start__lte', result.attributes.variant.pos], // jshint ignore:line
                                                ['position_end__gte', result.attributes.variant.pos] // jshint ignore:line
                                            ]
                                        }
                                ]
                            }]
                        }
                    );
                });
            }

        }

    });

    return {
        ResultDetailsModal: ResultDetailsModal
    };

});
