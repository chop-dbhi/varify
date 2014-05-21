/* global define */

define([
    'underscore',
    'backbone',
    '../utils'
], function(_, Backbone, utils) {

    var Phenotype = Backbone.Model.extend({
        lowestPriority: 10,
        highestPriority: 1,

        urlRoot: function() {
            var path = 'api/samples/' + this.get('sampleId') + '/phenotypes/';
            return utils.toAbsolutePath(path);
        },

        parsePriority: function(value) {
            return parseInt(value.priority, 10) || this.lowestPriority;
        },

        parse: function(attrs) {
            var path, lastModified, phenotypeModified;

            if (attrs.hpoAnnotations && attrs.hpoAnnotations.length) {
                attrs.hpoAnnotations =
                    _.sortBy(attrs.hpoAnnotations, this.parsePriority);
            }

            if (attrs.confirmedDiagnoses && attrs.confirmedDiagnoses.length) {
                attrs.confirmedDiagnoses =
                    _.sortBy(attrs.confirmedDiagnoses, this.parsePriority);
            }

            if (attrs.suspectedDiagnoses && attrs.suspectedDiagnoses.length) {
                attrs.suspectedDiagnoses =
                    _.sortBy(attrs.suspectedDiagnoses, this.parsePriority);
            }

            if (attrs.ruledOutDiagnoses && attrs.ruledOutDiagnoses.length) {
                attrs.ruledOutDiagnoses =
                    _.sortBy(attrs.ruledOutDiagnoses, this.parsePriority);
            }

            // Update pedigree path to point to the varify endpoint
            if (attrs.pedigree) {
                path = attrs.pedigree;
                path = path.replace('/phenotype/media', 'api/samples');
                attrs.pedigree = utils.toAbsolutePath(path);

                // Update the thumbnail path
                if (attrs.pedigree_thumbnail) { // jshint ignore: line
                    path = attrs.pedigree_thumbnail; // jshint ignore: line
                    path = path.replace('/phenotype/media', 'api/samples');
                    attrs.pedigree_thumbnail = utils.toAbsolutePath(path); // jshint ignore: line
                }
            }

            // Format the date properties if they are present
            lastModified = utils.parseISO8601UTC(attrs.last_modified);  // jshint ignore: line
            if (lastModified) {
                attrs.last_modified = lastModified.toLocaleString();    // jshint ignore: line
            }
            else {
                attrs.last_modified = "N/A";    // jshint ignore: line
            }

            phenotypeModified = utils.parseISO8601UTC(attrs.phenotype_modified);    // jshint ignore: line
            if (phenotypeModified) {
                attrs.phenotype_modified = phenotypeModified.toLocaleString();  // jshint ignore: line
            }
            else {
                attrs.phenotype_modified = "N/A";   // jshint ignore: line
            }

            return attrs;
        }
    });

    return {
        Phenotype: Phenotype
    };
});
