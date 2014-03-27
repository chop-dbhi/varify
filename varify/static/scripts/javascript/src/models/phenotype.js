/* global define */

define([
    'backbone',
    '../utils'
], function(Backbone, utils) {

    var Phenotype = Backbone.Model.extend({
        lowestPriority: 10,
        highestPriority: 1,

        urlRoot: function() {
            var path = 'api/samples/' + this.get('sample_id') + '/phenotypes/';
            return utils.toAbsolutePath(path);
        },

        parsePriority: function(value) {
            return parseInt(value.priority, 10) || this.lowestPriority + 1;
        },

        parse: function(attrs) {
            var path, lastModified, phenotypeModified;
            //Backbone.Model.prototype.parse.call(this, attrs);

            if (attrs.hpoAnnotations && attrs.hpoAnnotations.length) {
                attrs.hpoAnnotations = _.sortBy(attrs.hpoAnnotations, parsePriority);
            }

            if (attrs.confirmedDiagnoses && attrs.confirmedDiagnoses.length) {
                attrs.confirmedDiagnoses = _.sortBy(attrs.confirmedDiagnoses, parsePriority);
            }

            if (attrs.suspectedDiagnoses && attrs.suspectedDiagnoses.length) {
                attrs.suspectedDiagnoses = _.sortBy(attrs.suspectedDiagnoses, parsePriority);
            }

            if (attrs.ruledOutDiagnoses && attrs.ruledOutDiagnoses.length) {
                attrs.ruledOutDiagnoses = _.sortBy(attrs.ruledOutDiagnoses, parsePriority);
            }

            // Update pedigree path to point to the varify endpoint
            if (attrs.pedigree) {
                path = attrs.pedigree;
                path = path.replace('/phenotype/media', 'api/samples');
                attrs.pedigree = utils.toAbsolutePath(path);
            }

            // Format the date properties if they are present
            lastModified = utils.parseISO8601UTC(attrs.last_modified);
            if (lastModified) {
                attrs.last_modified = lastModified.toLocaleString();
            }
            else {
                attrs.last_modified = "N/A";
            }

            phenotypeModified = utils.parseISO8601UTC(attrs.phenotype_modified);
            if (phenotypeModified) {
                attrs.phenotype_modified = phenotypeModified.toLocaleString();
            }
            else {
                attrs.phenotype_modified = "N/A";
            }

            return attrs;
        }
    });

    return {
        Phenotype: Phenotype
    };
});
