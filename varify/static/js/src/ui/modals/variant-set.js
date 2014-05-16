/* global define */

define([
    'jquery',
    'underscore',
    'cilantro',
    'marionette'
], function($, _, c, Marionette) {

    var VariantSetDialog = Marionette.ItemView.extend({
        id: 'variant-set-dialog',

        className: 'modal hide',

        template: 'varify/modals/variant-set',

        ui: {
            close: '[data-target=close]',
            createdName: '[data-target=created-name]',
            description: '[data-target=description]',
            error: '[data-target=error-message]',
            fileChooser: '[data-target=file]',
            fileChooserContainer: '[data-target=file-container]',
            form: 'form',
            invalidContainer: '[data-target=invalid-container]',
            invalidCount: '[data-target=invalid-count]',
            invalidTable: '[data-target=invalid-table]',
            loading: '[data-target=loading-message]',
            name: '[data-target=name]',
            save: '[data-target=save]',
            sourceRadios: 'input[name=source]',
            successMessage: '[data-target=success-message]',
            validCount: '[data-target=valid-count]'
        },

        events: {
            'change @ui.sourceRadios': 'onSourceChange',
            'change input': 'onInputChange',
            'keyup input': 'onInputChange',
            'click @ui.close': 'close',
            'click @ui.save': 'save'
        },

        initialize: function() {
            _.bindAll(this, 'onSuccess', 'onError', 'close');
        },

        _reset: function() {
            // Reset the intial state of the UI
            this.$('input:not([type=radio])').val('');
            this.ui.sourceRadios.prop('checked', false);
            this.ui.sourceRadios.filter('[value=file]').prop('checked', true);
            this.ui.fileChooserContainer.show();

            this.ui.loading.hide();
            this.ui.error.hide();
            this.ui.successMessage.hide();
            this.ui.form.show();
        },

        close: function() {
            this._reset();
            this.$el.modal('hide');
        },

        open: function(sample) {
            this.sample = sample;
            this.$el.modal('show');
        },

        onInputChange: function() {
            var disabled = false;

            if (!this.ui.name.val()) {
                disabled = true;
            }

            if (this.ui.sourceRadios.filter(':checked').val() === 'file' &&
                    !this.ui.fileChooser.val()) {
                disabled = true;
            }

            this.ui.save.prop('disabled', disabled);
        },

        onSourceChange: function(event) {
            if (event.target.value === 'file') {
                this.ui.fileChooserContainer.show();
            }
            else {
                this.ui.fileChooserContainer.hide();
            }
        },

        onRender: function() {
            this.$el.modal({
                backdrop: 'static',
                keyboard: false,
                show: false
            });
        },

        onSuccess: function(model) {
            this.ui.createdName.text(model.get('name'));
            this.ui.validCount.text(model.get('count'));

            var invalidRecords = model.get('invalid_records');
            if (invalidRecords && invalidRecords.length) {
                this.ui.invalidCount.text(invalidRecords.length);

                var html = [], record;

                for (var i = 0; i < invalidRecords.length; i++) {
                    record = invalidRecords[i];

                    html.push('<tr>');
                    html.push('<td>' + record.chr + '</td>');
                    html.push('<td>' + record.start + '</td>');
                    html.push('<td>' + record.ref + '</td>');
                    html.push('<td>' + record.allele1 + '</td>');
                    html.push('<td>' + record.allele2 + '</td>');
                    html.push('<td>' + record.dbsnp + '</td>');
                    html.push('</tr>');
                }

                this.ui.invalidTable.html(html.join(''));

                this.ui.invalidContainer.show();
            }
            else {
                this.ui.invalidContainer.hide();
            }

            // If the modal is still open, then show a message informing the
            // user of the successful creation and then close the window after
            // a short delay. If the modal is closed, then use Cilantro's
            // notify feature to tell the user about the new variant set.
            if (this.$el.hasClass('in')) {
                this.ui.loading.hide();
                this.ui.successMessage.show();
            }
            else {
                c.notify({
                    header: 'Variant Set Created',
                    level: 'info',
                    timeout: 5000,
                    message: this.ui.successMessage.html()
                });
            }
        },

        onError: function() {
            // If the modal is still open, then show the user the error
            // message and hide the loader. If the modal is closed, use
            // Cilantro's notify feature to tell the user about the error
            // in creating their variant set.
            if (this.$el.hasClass('in')) {
                // TODO: Tailor the error message to the create type(file vs. filters)
                this.ui.loading.hide();
                this.ui.error.show();
            }
            else {
                // Don't timeout the error, we want to make sure the user sees
                // it so we force them to manually dismiss it.
                c.notify({
                    header: 'Error Creating Variant Set',
                    level: 'error',
                    timeout: false,
                    message: this.ui.error.text()
                });
            }
        },

        /* jshint ignore:start */
        /*
         * This code based on example here:
         *      http://estebanpastorino.com/2013/09/27/simple-file-uploads-with-backbone-dot-js/
         *
         */
        /* jshint ignore:end */
        save: function(event) {
            event.preventDefault();

            // Don't let the user trigger a duplicate save request
            this.ui.save.prop('disabled', true);

            this.ui.form.hide();
            this.ui.loading.show();

            var values = {
                name: this.ui.name.val(),
                description: this.ui.description.val()
            };

            var options = {
                wait: true,
                success: this.onSuccess,
                error: this.onError
            };

            if (this.ui.sourceRadios.filter(':checked').val() === 'file') {
                var formData = new FormData();
                var file = this.ui.fileChooser.prop('files')[0];

                formData.append('source', file, file.name);
                formData.append('name', this.ui.name.val());
                formData.append('description', this.ui.description.val());

                options = _.extend(options, {
                    data: formData,
                    // Prevent jQuery from converting files to strings
                    processData: false,
                    // Override default jQuery content type which seems to
                    // block file uploads.
                    contentType: false,
                });
            }

            this.sample.variantSets.create(values, options);
        }
    });

    return {
        VariantSetDialog: VariantSetDialog
    };

});
