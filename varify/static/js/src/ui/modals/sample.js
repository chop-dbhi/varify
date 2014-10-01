/* global define */

define([
    'jquery',
    'underscore',
    'marionette',
    'cilantro',
    '../sample'
], function($, _, Marionette, c, sample) {


    var SampleRow = sample.SampleView.extend({
        tagName: 'tr',

        template: 'varify/sample/row',

        modelEvents: {
            'change:selected': 'renderSelected',
            'change:filtered': 'renderFiltered'
        },

        events: {
            click: 'triggerSelected'
        },

        renderSelected: function() {
            this.$el.toggleClass('selected', !!this.model.get('selected'));
        },

        renderFiltered: function() {
            this.$el.toggleClass('filtered', !!this.model.get('filtered'));
        },

        triggerSelected: function(event) {
            event.preventDefault();
            event.stopPropagation();

            if (this.model.get('selected')) {
                this.model.trigger('deselect', this.model);
            }
            else {
                this.model.trigger('select', this.model);
            }
        },

        onRender: function() {
            this.renderSelected();
            this.renderFiltered();
        }
    });


    var SampleTable = Marionette.CompositeView.extend({
        template: 'varify/sample/table',

        itemView: SampleRow,

        itemViewContainer: 'tbody',

        ui: {
            input: 'input',
            loader: '[data-target=loader]'
        },

        events: {
            'input @ui.input': '_handleFilter',
            'click thead th': 'handleSort'
        },

        collectionEvents: {
            'sort': '_renderChildren',
            'reset': 'handleFilter hideLoader'
        },

        initialize: function() {
            this._handleFilter = _.debounce(this.handleFilter, c.INPUT_DELAY);
        },

        onRender: function() {
            var _this = this;

            _.defer(function() {
                _this.ui.input.focus();
            });
        },

        hideLoader: function() {
            // If we have been "closed" then there are no samples so we can
            // safely ignore the events that led us here.
            if (this.isClosed) return;

            this.ui.loader.hide();
        },

        handleFilter: function() {
            // If we have been "closed" then there are no samples so we can
            // safely ignore the events that led us here.
            if (this.isClosed) return;

            this.applyFilter(this.ui.input.val());
        },

        handleSort: function(event) {
            if (!this.collection.length) return;

            this.applySort($(event.target).data('sort'));
        },

        applyFilter: function(value) {
            var regexp = new RegExp(value, 'i');

            this.collection.each(function(model) {
                var filtered = true;

                if (regexp.test(model.get('label'))) {
                    filtered = false;
                }
                else if (regexp.test(model.get('batch'))) {
                    filtered = false;
                }
                else if (regexp.test(model.get('project'))) {
                    filtered = false;
                }

                model.set('filtered', filtered);
            });
        },

        applySort: function(attr) {
            var dir = 'asc';

            // Already sorted by the attribute, cycle direction
            if (this.collection._sortAttr === attr) {
                dir = this.collection._sortDir === 'asc' ? 'desc' : 'asc';
            }

            this.$('[data-sort=' + this.collection._sortAttr + ']')
                .removeClass(this.collection._sortDir);
            this.$('[data-sort=' + attr + ']').addClass(dir);

            // Reference for cycling
            this.collection._sortAttr = attr;
            this.collection._sortDir = dir;

            // Parse function for handling the different sort attributes.
            var parse;

            if (attr === 'created') {
                parse = function(v) {
                    return (new Date(v)).getTime();
                };
            }
            else {
                parse = function(v) {
                    return v;
                };
            }

            this.collection.comparator = function(m1, m2) {
                var v1 = parse(m1.get(attr)),
                    v2 = parse(m2.get(attr));

                if (v1 < v2) return (dir === 'asc' ? 1 : -1);
                if (v1 > v2) return (dir === 'asc' ? -1 : 1);

                return 0;
            };

            this.collection.sort();
        }
    });


    var SampleDialog = Marionette.Layout.extend({
        id: 'sample-dialog',

        className: 'modal hide',

        template: 'varify/modals/sample',

        regions: {
            samples: '[data-target=samples-region]'
        },

        ui: {
            empty: '[data-target=empty-message]',
            selectedSample: '[data-target=selected-sample]',
            cancelButton: '.cancel-button',
            saveButton: '[data-target=save]',
            clearButton: '.clear-button'
        },

        events: {
            'click @ui.cancelButton': 'cancelAndClose',
            'click @ui.saveButton': 'handleSaveSample',
            'click @ui.clearButton': 'clearSelected'
        },

        regionViews: {
            samples: SampleTable
        },

        initialize: function() {
            this.data = {};

            if (!(this.data.context = this.options.context)) {
                throw new Error('context model required');
            }

            if (!(this.data.samples = this.options.samples)) {
                throw new Error('samples collection required');
            }

            // Define (get or create) the internal filter for the sample concept
            this.data.filter = this.data.context.define({
                concept: c.config.get('varify.sample.concept'),
                field: c.config.get('varify.sample.field')
            });

            // Flag the currently selected sample if one exists onces the samples
            // load
            this.listenTo(this.data.samples, 'reset', this.onSamplesReset);
            this.listenTo(this.data.samples, 'select', this.setSelected);
            this.listenTo(this.data.samples, 'deselect', this.setDeselected);
        },

        onRender: function() {
            this.$el.modal({
                backdrop: 'static',
                keyboard: false,
                show: false
            });

            var samples = new this.regionViews.samples({
                collection: this.data.samples
            });

            this.samples.show(samples);
        },

        onSamplesReset: function() {
            if (this.data.samples.length === 0) {
                this.samples.close();
                this.ui.empty.show();
            }
            else {
                this.getSelected();
            }
        },

        // Select an individual sample given a value representing that sample.
        // This handles all cases from the current(where the value is a number
        // being the sample id) to legacy cases where the values were object
        // or string based. In legacy cases, the context will be updated to
        // use the new format and that change will be persisted when the
        // sample selection is saved.
        _selectSample: function(value) {
            var model;

            if (value) {
                // Parse { value: ..., label: ... } format
                if (typeof value === 'object') value = value.value;

                // Find by id if value is a number, otherwise assume the label
                if (typeof value === 'number') {
                    model = this.data.samples.get(value);
                }
                else {
                    model = this.data.samples.findWhere({label: value});
                    // Ensure the value is only sample id. This is primarily to
                    // migrate legacy filters to the new format.
                    if (model) {
                        this.data.filter.set('value', model.id, {trigger: false});
                    }
                }
            }

            if (model) {
                this.data.samples.trigger('select', model);
            }
        },

        // Get the currently selected samples from the context and updates the
        // state of the collection.
        getSelected: function() {
            var value = this.data.filter.get('value'),
                operator = this.data.filter.get('operator');

            if (operator === 'in') {
                var _this = this;

                _.each(value, function(v) {
                    _this._selectSample(v);
                });
            }
            else {
                this._selectSample(value);
            }
        },

        clearSelected: function() {
            this.data.samples.each(function(sample) {
                sample.set('selected', false);
            });

            this.renderSelectedSamples();
        },

        setDeselected: function(model) {
            this.data.samples.get(model.id).set('selected', false);
            this.renderSelectedSamples();
        },

        setSelected: function(model) {
            this.data.samples.each(function(m) {
                m.set('selected', m.get('selected') || m.id === model.id);
            });

            this.renderSelectedSamples();
        },

        _getSampleHtml: function(sample) {
            return '<li><strong>' + sample.get('label') +
                    '</strong> from project <strong>' +
                    sample.get('project') + ' (' + sample.get('batch') +
                    ')</strong></li>';
        },

        renderSelectedSamples: function() {
            var models = this.data.samples.where({selected: true});

            var html;

            if (!models.length) {
                html = '<p><strong>Please select a sample.</strong></p>';
            }
            else {
                var _this = this;

                var sampleHtml = _.map(models, function(sample) {
                    return _this._getSampleHtml(sample);
                });

                html = '<ul class=unstyled>' + sampleHtml.join('') + '</ul>';
            }

            this.ui.selectedSample.html(html);
            this.ui.saveButton.prop('disabled', !models);
        },

        cancelAndClose: function() {
            this.getSelected();
            this.close();
        },

        handleSaveSample: function(event) {
            event.preventDefault();

            var ids = _.pluck(this.data.samples.where({selected: true}), 'id');

            this.data.filter.set({
                operator: 'in',
                value: ids
            });

            if (this.data.filter.hasChanged()) {
                this.data.filter.apply();
            }
            this.close();
        },

        open: function() {
            this.$el.modal('show');
        },

        close: function() {
            this.$el.modal('hide');
        }
    });


    return {
        SampleDialog: SampleDialog
    };

});
