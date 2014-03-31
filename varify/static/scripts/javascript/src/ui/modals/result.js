/* global define */

define([
    'jquery',
    'underscore',
    'marionette',
    'cilantro',
    '../../models',
    '../../utils',
    '../../templates',
], function($, _, Marionette, c, models, utils, Templates) {

    var DetailsTab = Marionette.ItemView.extend({
        template: function() {},

        initialize: function() {
            _.bindAll(this, 'fetchMetricsError', 'fetchMetricsSuccess');

            this.metrics = this.options.metrics;

            this.$content = $('<div class=content>');
            this.$el.append(this.$content);
            this.$el.attr('id', 'variant-details-content');
        },

        events: {
            'click .cohort-sample-popover': 'hidePopover',
            'click .assessment-details-table .icon-plus': 'expandAssessmentRow',
            'click .assessment-details-table .icon-minus': 'collapseAssessmentRow'
        },

        hidePopover: function(event) {
            $('.cohort-sample-popover').not(event.target).popover('hide');
        },

        expandAssessmentRow: function(event) {
            // Figure out which row we clicked on.
            var row = $(event.target).closest('tr');

            // Lookup the details row.
            var detailsRow = $('#' + row.attr('id') + '-details');

            // Hide the expand(+) control, show the collapse(-) control, and
            // show the details row.
            detailsRow.show();
            $(event.target).addClass('hide');
            row.find('.icon-minus').removeClass('hide');
        },

        collapseAssessmentRow: function(event) {
            // Figure out which row we clicked on.
            var row = $(event.target).closest('tr');

            // Lookup the details row.
            var detailsRow = $('#' + row.attr('id') + '-details');

            // Show the expand(+) control, hide the collapse(-) control, and
            // hide the details row.
            detailsRow.hide();
            $(event.target).addClass('hide');
            row.find('.icon-plus').removeClass('hide');
        },

        renderCohorts: function(attrs) {
            var content = [];
            content.push('<h4>Cohorts</h4>');

            if ((attrs.cohorts != null) && attrs.cohorts.length) {
                content.push('' + Templates.cohortVariantDetailList(attrs.cohorts));
            }
            else {
                content.push('<p class=muted>No cohorts</p>');
            }

            return content.join('');
        },

        renderPredictions: function(attrs) {
            var content, labelClass, pp2, sift;

            content = [];
            content.push('<h4>Prediction Scores</h4>');
            content.push('<ul class=unstyled>');

            if ((sift = attrs.sift[0])) {
                labelClass = '';

                switch (sift.prediction) {
                    case 'Damaging':
                        labelClass = 'text-error';
                        break;
                    default:
                        labelClass = 'muted';
                }

                content.push('<li><small>SIFT</small> <span class=' +
                    labelClass + '>' + sift.prediction + '</span></li>');
            }

            if ((pp2 = attrs.polyphen2[0])) {
                labelClass = '';

                switch (pp2.prediction) {
                    case 'Probably Damaging':
                        labelClass = 'text-error';
                        break;
                    case 'Possibly Damaging':
                        labelClass = 'text-warning';
                        break;
                    default:
                        labelClass = 'muted';
                }

                content.push('<li><small>PolyPhen2</small> <span class=' +
                    labelClass + '>' + pp2.prediction + '</span></li>');
            }

            content.push('</ul>');

            if (!(sift || pp2)) {
                content.push('<p class=muted>No predictions scores</p>');
            }

            return content.join('');
        },

        renderSummary: function(resultAttrs, variantAttrs) {
            var bases, content, hgmdLinks, key, labelClass;

            content = [];
            content.push('<h4>' + resultAttrs.sample.label + ' <small>in ' +
                resultAttrs.sample.project + '</small></h4>');
            content.push('<ul class=unstyled>');
            content.push('<li><small>Variant Result ID </small>' +
                resultAttrs.id + '</li>');

            labelClass = utils.depthClass(resultAttrs.read_depth);
            content.push('<li><small>Coverage</small> <span class=' +
                labelClass + '>' + resultAttrs.read_depth +
                'x</span> <span class=muted>(<span title=Ref>' +
                resultAttrs.read_depth_ref + '</span>/<span title=Alt>' +
                resultAttrs.read_depth_alt + '</span>)</span> </li>');
            content.push('<li><small>Raw Coverage</small> ');

            if (resultAttrs.raw_read_depth != null) {
                content.push('' + resultAttrs.raw_read_depth + 'x');
            }
            else {
                content.push('<span class=muted>n/a</span>');
            }

            content.push('</li>');

            labelClass = utils.qualityClass(resultAttrs.quality);
            content.push('<li><small>Quality</small> <span class=' +
                labelClass + '>' + resultAttrs.quality + '</span> </li>');
            content.push('<li style=word-wrap:break-word><small>Genotype</small> ' +
                resultAttrs.genotype_value + ' <small>(' +
                resultAttrs.genotype_description + ')</small></li>');
            content.push('<li><small>Base Counts</small> ');

            if (resultAttrs.base_counts) {
                bases = [];

                for (key in resultAttrs.base_counts) {
                    bases.push('' + key + '=' + resultAttrs.base_counts[key]);
                }

                content.push(bases.sort().join(', '));
            }
            else {
                content.push('<span class=muted>n/a</span>');
            }

            content.push('</li>');
            content.push('<li><small>Position</small> ' +
                (Templates.genomicPosition(variantAttrs.chr, variantAttrs.pos)) +
                '</li>');
            content.push('<li><small>Genes</small> ' +
                (Templates.geneLinks(variantAttrs.uniqueGenes)) + '</li>');

            hgmdLinks = Templates.hgmdLinks(variantAttrs.phenotypes);
            if (hgmdLinks) {
                content.push('<li><small>HGMD IDs</small> ' + hgmdLinks + '</li>');
            }

            if (variantAttrs.rsid) {
                content.push('<li><small>dbSNP</small> ' +
                    (Templates.dbSNPLink(variantAttrs.rsid)) + '</li>');
            }

            content.push('</ul>');
            content.push('<a href="http://localhost:10000/show?request=chr' +
                variantAttrs.chr + ':g.' + variantAttrs.pos +
                variantAttrs.ref + '>' + variantAttrs.alt +
                '" target=_blank class="btn btn-primary btn-small alamut-button">Query Alamut</a>');

            return content.join('');
        },

        renderFrequencies: function(attrs) {
            var content, evs, tg;

            content = [];
            content.push('<h4>1000 Genomes</h4>');

            if ((tg = attrs['1000g'][0])) {
                content.push('<ul class=unstyled>');

                if (tg.all_af != null) {
                    content.push('<li><small>All</small> ' + (c.utils.prettyNumber(tg.all_af * 100)) + '%</li>');
                }
                if (tg.amr_af != null) {
                    content.push('<li><small>American</small> ' + (c.utils.prettyNumber(tg.amr_af * 100)) + '%</li>');
                }
                if (tg.afr_af != null) {
                    content.push('<li><small>African</small> ' + (c.utils.prettyNumber(tg.afr_af * 100)) + '%</li>');
                }
                if (tg.eur_af != null) {
                    content.push('<li><small>European</small> ' + (c.utils.prettyNumber(tg.eur_af * 100)) + '%</li>');
                }

                content.push('</ul>');
            }
            else {
                content.push('<p class=muted>No 1000G frequencies</p>');
            }

            content.push('<h4 title="Exome Variant Server">EVS</h4>');
            if ((evs = attrs.evs[0])) {
                content.push('<ul class=unstyled>');

                if (evs.all_af != null) {
                    content.push('<li><small>All</small> ' + (c.utils.prettyNumber(evs.all_af * 100)) + '%</li>');
                }
                if (evs.afr_af != null) {
                    content.push('<li><small>African</small> ' + (c.utils.prettyNumber(evs.afr_af * 100)) + '%</li>');
                }
                if (evs.eur_af != null) {
                    content.push('<li><small>European</small> ' + (c.utils.prettyNumber(evs.eur_af * 100)) + '%</li>');
                }

                content.push('</ul>');
            }
            else {
                content.push('<p class=muted>No EVS frequencies</p>');
            }

            return content.join('');
        },

        renderEffects: function(attrs) {
            var content, eff, effs, gene, labelClass, type, hasEffects, groupedEffects;

            content = [];
            content.push('<h4>Effects</h4>');

            hasEffects = false;
            _.each(attrs.effects, function(eff) {
                if (eff.transcript != null) hasEffects = true;
            });

            if (hasEffects) {
                content.push('<ul class=unstyled>');

                groupedEffects = _.groupBy(attrs.effects, 'type');
                for (type in groupedEffects) {
                    effs = groupedEffects[type];

                    content.push('<li>');

                    labelClass = utils.priorityClass(utils.effectImpactPriority(effs[0].impact));
                    content.push('<span class=' + labelClass + '>' + type + '</span>');

                    content.push('<ul>');

                    for (var i = 0; i < effs.length; i++) {
                        eff = effs[i];

                        content.push('<li>');
                        content.push('<small><a href="http://www.ncbi.nlm.nih.gov/nuccore/' +
                            eff.transcript.transcript + '">' +
                            eff.transcript.transcript + '</a></small> ');

                        if (attrs.uniqueGenes.length > 1 && (gene = eff.transcript.gene)) {
                          content.push('<small>for <a target=_blank href="http://www.genenames.org/data/hgnc_data.php?hgnc_id=' + gene.hgnc_id + '">' + gene.symbol + '</a></small> ');
                        }

                        content.push('<ul><li>');

                        if (eff.hgvs_c) {
                            content.push('' + eff.hgvs_c + ' ');
                        }
                        if (eff.segment) {
                            content.push('' + eff.segment + ' ');
                        }

                        content.push('</li>');

                        if (eff.hgvs_p || eff.amino_acid_change) {
                            content.push('<li>' + (eff.hgvs_p || eff.amino_acid_change) + '</li>');
                        }

                        content.push('</ul>');
                    }

                    content.push('</li></ul>');
                }

                content.push('</ul>');
            }
            else {
                content.push('<p class=muted>No SNPEff effects known</p>');
            }

            return content.join('');
        },

        _renderPhenotypeCollection: function(phenotypes) {
            var content, phenotype, sorted, zpad;

            content = [];

            sorted = _.sortBy(phenotypes, function(item) {
                return item.term;
            });

            content.push('<ul>');

            for (var i = 0; i < sorted.length; i++) {
                phenotype = sorted[i];
                content.push('<li>' + phenotype.term);

                if (phenotype.hpo_id || phenotype.hgmd_id) {
                    if (phenotype.hgmd_id) {
                        content.push(' (HGMD: ' + phenotype.hgmd_id + ')');
                    }
                    if (phenotype.hpo_id) {
                        // Zero-pad the HPO ID to force it to be 7 digits. This
                        // trick is from:
                        //       http://dev.enekoalonso.com/2010/07/20/little-tricks-string-padding-in-javascript/
                        zpad = String('0000000' + phenotype.hpo_id).slice(-7);
                        content.push(' (<a href="http://www.human-phenotype-ontology.org/hpoweb/showterm?id=HP_' + zpad + '">HPO: ' + zpad + '</a>)');
                    }
                }

                content.push('</li>');
            }

            content.push('</ul>');
            return content;
        },

        renderPhenotypes: function(attrs) {
            var content = [];

            content.push('<h4>Phenotypes</h4>');

            if (attrs.phenotypes[0]) {
                content.push('<ul class=unstyled>');
                content.push('<li>Variant:</li>');
                content = content.concat(this._renderPhenotypeCollection(attrs.phenotypes));
                content.push('</ul>');
            }
            else {
                content.push('<p class=muted>No associated variant phenotypes</p>');
            }

            if (attrs.uniqueGenes[0]) {
                content.push('<ul class=unstyled>');

                _.each(attrs.uniqueGenes, function(gene) {
                    content.push('<li>' + gene.symbol + ':</li>');

                    if (gene.phenotypes[0]) {
                        content = content.concat(this._renderPhenotypeCollection(gene.phenotypes));
                    }
                    else {
                        content.push('<p class=muted>No phenotypes for this gene</p>');
                    }
                }, this);

                content.push('</ul>');
            }

            return content.join('');
        },

        _renderClinVarCollection: function(assertions) {
            var assertion;
            var content = [];

            for (var i = 0; i < assertions.length; i++) {
                assertion = assertions[i];
                content.push("<li>Assertion: <a target=\"_blank\" href=\"https://www.ncbi.nlm.nih.gov/clinvar/" + assertion.rcvaccession + "/\">" + assertion.rcvaccession + "</a>");
                content.push('<ul>');
                content.push("<li><small>Siginificance</small> <b>" + assertion.clinicalsignificance + "</b></li>");
                content.push("<li><small>Origin</small> " + assertion.origin + "</li>");
                content.push("<li><small>Type</small> " + assertion.type + "</li>");
                content.push("<li><small># Submitters</small> " + assertion.numbersubmitters + "</li>");
                content.push("<li><small>Review Status</small> " + assertion.reviewstatus + "</li>");
                content.push("<li><small>Last Evaluated</small> " + assertion.lastevaluated + "</li>");
                content.push('</ul>');
                content.push('</li>');
            }

            return content;
        },

        renderClinVar: function(attrs) {
            var content = [];

            content.push('<h4>ClinVar</h4>');

            if (attrs.solvebio.clinvar[0]) {
                content.push('<ul class=unstyled>');
                content = content.concat(this._renderClinVarCollection(attrs.solvebio.clinvar));
                content.push('</ul>');
            } else {
                content.push('<p class=muted>No ClinVar assertions</p>');
            }

            return content.join('');
        },

        _renderArticleCollection: function(articles) {
            var content, pmid, sorted;

            content = [];
            sorted = _.sortBy(articles, function(item) {
                return item;
            });

            content.push('<ul>');

            for (var i = 0; i < sorted.length; i++) {
                pmid = sorted[i];
                content.push('<li><a href="http://www.ncbi.nlm.nih.gov/pubmed/' + pmid + '">' + pmid + '</a></li>');
            }

            content.push('</ul>');
            return content;
        },

        renderPubmed: function(attrs) {
            var content = [];

            content.push('<h4>Articles</h4>');

            if (attrs.articles[0]) {
                content.push('<ul class=unstyled>');
                content.push('<li>Variant:</li>');
                content = content.concat(this._renderArticleCollection(attrs.articles));
                content.push('</ul>');
            }
            else {
                content.push('<p class=muted>No PubMed articles for this variant</p>');
            }

            if (attrs.uniqueGenes[0]) {
                content.push('<ul class=unstyled>');

                _.each(attrs.uniqueGenes, function(gene) {
                    content.push("<li>" + gene.symbol + ":</li>");

                    if (gene.articles[0]) {
                        content = content.concat(this._renderArticleCollection(gene.articles));
                    }
                    else {
                        content.push('<p class=muted>No PubMed articles for this gene</p>');
                    }
                }, this);

                content.push('</ul>');
            }

            return content.join('');
        },

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

        _renderExpandCollapse: function() {
            var content = [];

            content.push('<div class=expand-collapse-container>');
            content.push('<a href="#" data-target=expand-collapse-link>MORE</a>');
            content.push('</div>');

            return content.join('');
        },

        _span: function(html, size) {
            if (size == null) {
                size = 12;
            }

            return $('<div class="span' + size + '" />').html(html);
        },

        render: function() {
            var $row1, $row2, $row3, attrs;

            attrs = this.model.get('variant');

            $row1 = $('<div class=row-fluid data-target=expandable-details-row />');
            $row2 = $('<div class=row-fluid data-target=expandable-details-row />');
            $row3 = $('<div class="row-fluid  assessments-table-container" />');

            $row1.append(this._span(this.renderSummary(this.model.attributes, attrs), 3));
            $row1.append(this._span(this.renderEffects(attrs), 3).addClass('expandable-details-item').append(this._renderExpandCollapse));
            $row1.append(this._span(this.renderPhenotypes(attrs), 3).addClass('expandable-details-item').append(this._renderExpandCollapse));
            $row1.append(this._span(this.renderPredictions(attrs), 3));

            $row2.append(this._span(this.renderCohorts(attrs), 3).addClass('expandable-details-item').append(this._renderExpandCollapse));
            $row2.append(this._span(this.renderFrequencies(attrs), 3));
            $row2.append(this._span(this.renderPubmed(attrs), 3).addClass('expandable-details-item').append(this._renderExpandCollapse));

            if (attrs['solvebio']) {
                $row2.append(this._span(this.renderClinVar(attrs), 3).addClass('expandable-details-item').append(this._renderExpandCollapse));
            }

            $row3.append(this._span(this.renderAssessmentMetricsContainer(), 12));

            this.$content.append($row1, $row2, $row3);
            this.$el.find('.cohort-sample-popover').popover();
            this.metrics.fetch({
                success: this.fetchMetricsSuccess,
                error: this.fetchMetricsError
            });

            return this.$el;
        }

    });

    var AssessmentTab = Marionette.ItemView.extend({
        template: function () {},

        el: '#knowledge-capture-content',

        initialize: function() {
            _.bindAll(this, 'onAssessmentFetchSuccess', 'onAssessmentFetchError');
        },

        update: function(model) {
            // If this is the first update call then we need to intialize the
            // UI elements so we can reference them in the success/error
            // handlers in the fetch call we are about to make.
            if (this.model == null) {
                this.formContainer = $('#knowledge-capture-form-container');
                this.feedbackContainer = $('#knowledge-capture-feedback-container');
                this.saveButton = $('#save-assessment-button');
                this.auditButton = $('#audit-trail-button');
                this.errorContainer = $('#error-container');
                this.errorMsg = $('#error-message');
                $('.alert-error > .close').on('click', this.closeFormErrorsClicked);
            }

            this.formContainer.hide();
            this.feedbackContainer.show();
            this.errorContainer.hide();

            this.model = model;
            this.model.fetch({
                error: this.onAssessmentFetchError,
                success: this.onAssessmentFetchSuccess
            });
        },

        onAssessmentFetchError: function() {
            this.formContainer.hide();
            this.feedbackContainer.hide();
            this.errorContainer.show();
            this.errorMsg.html('<h5 class=text-error>Error retrieving knowledge capture data.</h5>');
            this.saveButton.hide();
            return this.auditButton.hide();
        },

        onAssessmentFetchSuccess: function() {
            this.errorContainer.hide();
            this.feedbackContainer.hide();
            this.formContainer.show();
            return this.render();
        },

        closeFormErrorsClicked: function(event) {
            $(event.target).parent().hide();
        },

        isValid: function() {
            var valid = true;

            this.model.set({
                evidence_details: $('#evidence-details').val(),
                sanger_requested: $('input[name=sanger-radio]:checked').val(),
                pathogenicity: $('input[name=pathogenicity-radio]:checked').val(),
                assessment_category: $('input[name=category-radio]:checked').val(),
                mother_result: $('#mother-results').val(),
                father_result: $('#father-results').val()
            });

            this.errorContainer.hide();
            this.errorMsg.html('');

            if (_.isEmpty(this.model.get('pathogenicity'))) {
                valid = false;
                this.errorMsg.append('<h5>Please select a pathogenicity.</h5>');
            }

            if (_.isEmpty(this.model.get('assessment_category'))) {
                valid = false;
                this.errorMsg.append('<h5>Please select a category.</h5>');
            }

            if (_.isEmpty(this.model.get('mother_result'))) {
                valid = false;
                this.errorMsg.append('<h5>Please select a result from the &quot;Mother&quot; dropdown.</h5>');
            }

            if (_.isEmpty(this.model.get('father_result'))) {
                valid = false;
                this.errorMsg.append('<h5>Please select a result from the &quot;Father&quot; dropdown.</h5>');
            }

            if (this.model.get('sanger_requested') == null) {
                valid = false;
                this.errorMsg.append('<h5>Please select one of the &quot;Sanger Requested&quot; options.</h5>');
            }

            if (!valid) {
                this.errorContainer.show();
            }

            return valid;
        },

        // Checks the radio button with the supplied name and value(all other
        // radios with that name are unchecked).
        setRadioChecked: function(name, value) {
            var checkedRadio, radios;

            // Lookup all the radio buttons using the supplied name
            radios = $('input:radio[name=' + name + ']');
            // Uncheck any current selection
            $(radios.prop('checked', false));
            // Check the correct radio button based on the supplied value
            checkedRadio = $(radios.filter('[value=' + value + ']'));
            $(checkedRadio.prop('checked', true));
            $(checkedRadio.change());
        },

        render: function() {
            this.setRadioChecked('category-radio', this.model.get('assessment_category'));
            this.setRadioChecked('pathogenicity-radio', this.model.get('pathogenicity'));
            this.setRadioChecked('sanger-radio', this.model.get('sanger_requested'));

            $('#mother-results').val(this.model.get('mother_result'));
            $('#father-results').val(this.model.get('father_result'));
            $('#evidence-details').val(this.model.get('evidence_details'));
        }

    });

    var ResultDetails = Marionette.ItemView.extend({
        className: 'result-details-modal modal hide',

        // Fairly arbitray, mostly chosen because it was close to normal height
        // of the sample summary item(1st item in upper left).
        maxExpandableHeight: 300,
        showLessText: 'Show Less...',
        showMoreText: 'Show More...',

        template: 'varify/modals/result',

        ui: {
            variantDetailsTabContent: '#variant-details-content',
            saveButton: '#save-assessment-button',
            auditTrailButton: '#audit-trail-button'
        },

        events: {
            'click #close-review-button': 'close',
            'click #save-assessment-button': 'saveAndClose',
            'click #variant-details-link': 'hideButtons',
            'click #knowledge-capture-link': 'showButtons',
            'click [data-target=expand-collapse-link]': 'toggleExpandedState'
        },

        initialize: function() {
            this.assessmentTab = new AssessmentTab;
        },

        hideButtons: function() {
            this.ui.saveButton.hide();
            this.ui.auditTrailButton.hide();
        },

        showButtons: function() {
            this.ui.saveButton.show();
            this.ui.auditTrailButton.show();
        },

        saveAndClose: function(event) {
            if (this.assessmentTab.isValid()) {
                this.assessmentTab.model.save(null, {success: this.onSaveSuccess, error: this.onSaveError});
                this.close();
            }
        },

        close: function() {
            this.$el.modal('hide');
        },

        onSaveError: function(model, response) {
            $('#review-notification').html('Error saving knowledge capture data.');
            $('#review-notification').addClass('alert-error');
            this.showNotification();
        },

        onSaveSuccess: function(model, response) {
            $('#review-notification').html('Saved changes.');
            $('#review-notification').addClass('alert-success');
            this.showNotification();
            this.selectedSummaryView.model.fetch();
        },

        showNotification: function() {
            $('#review-notification').show();
            setTimeout(this.hideNotification, 5000);
        },

        hideNotification: function() {
            $('#review-notification').removeClass('alert-error alert-success');
            $('#review-notification').hide();
        },

        onRender: function() {
            this.$el.modal({
                show: false,
                keyboard: false,
                backdrop: 'static'
            })
        },

        /*
         * Reset state of all the expand/collapse links based on whether their
         * item is overflowing. Overflow detection code adapted from Mohsen's
         * answer here:
         *      http://stackoverflow.com/questions/7668636/check-with-jquery-if-div-has-overflowing-elements
         */
        _checkForOverflow: function() {
            _.each($('.expandable-details-item'), function(element) {
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

                    if ((child.offsetTop + child.offsetHeight) > this.maxExpandableHeight) {
                        hasOverflow = true;
                        break;
                    }
                }

                // We handle both cases because an item previously might have
                // have been bounded and is now overflown or vice-versa and we
                // want to match the current regardless of previous states.
                if (hasOverflow) {
                    $(element).find('.expand-collapse-container').show();
                }
                else {
                    $(element).find('.expand-collapse-container').hide();
                }

            }, this);
        },

        // Toggles the expanded/collapsed state of the row containing the item
        // containing the clicked link.
        toggleExpandedState: function(event) {
            var element, parent;

            element = $(event.target);
            parent = element.closest('[data-target=expandable-details-row]');

            // We essentially link all the expand/collapse links in a single
            // row to take the same action. So, when one is used to expand, all
            // other links in the row get updated in the same fasion to keep
            // them all in sync.
            if (element.text() === this.showMoreText) {
                parent.find('[data-target=expand-collapse-link]')
                      .text(this.showLessText);
                parent.css('height', 'auto')
                      .css('overflow', 'visible');
            }
            else {
                parent.find('[data-target=expand-collapse-link]')
                      .text(this.showMoreText);
                parent.css('height', this.maxExpandableHeight)
                      .css('overflow', 'hidden');
            }
        },

        open: function(summaryView, result) {
            var assessmentModel, metrics;

            this.selectedSummaryView = summaryView;
            this.model = result;

            metrics = new models.AssessmentMetrics({}, {
                variant_id: result.get('variant').id,
                result_id: result.id
            });

            this.detailsTab = new DetailsTab({
                model: result,
                metrics: metrics
            });

            this.ui.variantDetailsTabContent.html(this.detailsTab.render);

            // Create a new view for the knowledge capture form
            assessmentModel = new models.Assessment({
                sample_result: this.model.id
            });

            if (this.model.get('assessment') != null) {
                assessmentModel.id = this.model.get('assessment').id;
            }

            this.assessmentTab.update(assessmentModel);

            this.$el.modal('show');

            // Reset the row and item heights and overflow styles as they may
            // have been toggled previously.
            $('[data-target=expandable-details-row]').css('height', '' + this.maxExpandableHeight + 'px')
                .css('overflow', 'hidden');
            $('[data-target=expand-collapse-link]').text(this.showMoreText);

            this._checkForOverflow();
        }

    });

    return {
        ResultDetails: ResultDetails
    };

});
