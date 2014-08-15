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
            this.model.trigger('select', this.model);
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
            selectedSample: '.modal-footer [data-target=selected-sample]',
            saveButton: '[data-target=save]',
        },

        events: {
            'click @ui.saveButton': 'handleSaveSample'
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

        // Get the currently selected sample from the context and updates the
        // state of the collection.
        getSelected: function() {
            var value = this.data.filter.get('value'),
                operator = this.data.filter.get('operator');

            var model;

            if (value) {
                // Unpack in case the IN operator is being used
                if (operator === 'in') value = value[0];

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

            this.data.samples.trigger('select', model);
        },

        setSelected: function(model) {
            this.data.samples.each(function(m) {
                m.set('selected', model && m.id === model.id);
            });

            this.renderSelectedSample();
        },

        renderSelectedSample: function() {
            var model = this.data.samples.findWhere({selected: true});

            var html;

            if (model) {
                html = 'Current: <strong>' + model.get('label') +
                    '</strong> from project <strong>' +
                    model.get('project') + ' (' + model.get('batch') + ')</strong>';

            }
            else {
                html = 'Please select a sample.';
            }

            this.ui.selectedSample.html(html);
            this.ui.saveButton.prop('disabled', !model);
        },

        handleSaveSample: function(event) {
            event.preventDefault();

            var model = this.data.samples.findWhere({selected: true});

            this.data.filter.set({
                operator: 'exact',
                value: model.id
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
