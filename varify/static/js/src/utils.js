/* global define */

define([
    'underscore'
], function(_) {

    var depthClass = function(depth) {
        if (depth < 10) {
            return 'text-warning';
        }
        else if (depth >= 30) {
            return 'text-success';
        }
        else {
            return '';
        }
    };

    // Converts a list of values to a list of objects where the key for each
    // object is the supplied key and the value is the value from the list.
    var listToObjects = function(list, key) {
        var data = [], item;

        for (var i = 0; i < list.length; i++) {
            item = {};
            item[key] = list[i];
            data.push(item);
        }

        return data;
    };

    var groupArticlesByType = function(variant) {
        var data = [];

        data.push({
            type: 'variant',
            articles: listToObjects(variant.articles, 'id')
        });

        for (var i = 0; i < variant.uniqueGenes.length; i++) {
            data.push({
                type: 'gene',
                articles: listToObjects(variant.uniqueGenes[i].articles, 'id'),
                gene: variant.uniqueGenes[i]
            });
        }

        return data;
    };


    var groupEffectsByType = function(effects) {
        var data = [];

        if (effects && effects.length) {
            var groupedEffects = _.groupBy(effects, 'type');
            for (var type in groupedEffects) {
                data.push({
                    type: type,
                    effects: groupedEffects[type]
                });
            }
        }

        return data;
    };


    var groupPhenotypesByType = function(variant) {
        var data = [];

        data.push({
            type: 'variant',
            phenotypes: variant.phenotypes
        });

        for (var i = 0; i < variant.uniqueGenes.length; i++) {
            data.push({
                type: 'gene',
                phenotypes: variant.uniqueGenes[i].phenotypes,
                gene: variant.uniqueGenes[i]
            });
        }

        return data;
    };


    var effectImpactPriority = function(impact) {
        var priority;

        switch(impact) {
            case 'High':
                priority = 1;
                break;
            case 'Moderate':
                priority = 2;
                break;
            case 'Low':
                priority = 3;
                break;
            case 'Modifier':
                priority = 4;
                break;
            default:
                priority = 5;
                break;
        }

        return priority;
    };


    var getRootUrl = function() {
        /*
         * Get the route-free URL. That is, we want to remove the route at the
         * end of the URL and be left with the root URL so we can use this to
         * construct the result URLs later on. For example:
         *
         *  http://localhost/varify/results/  becomes  http://localhost/varify/
         *  http://localhost/variant-sets/1   becomes  http://localhost/
         */
        return window.location.href.replace(/\/[^\/]*\/([0-9]+)?$/, '/');
    };


    var parseISO8601UTC = function(str) {
        /*
         * This method assumes that the times are expressed in UTC with the
         * special 'Z' designator implied. That is, regardless of whether the
         * string ends in a 'Z' or not, it is assumed that it is in UTC format
         * as discussed in profile definition (1) here:
         *
         *       http://www.w3.org/TR/NOTE-datetime
         *
         * This method as no handling for cases where the times are expressed
         * in local time with a timezone offset. Additionally, this method
         * assumes that the time is complete, that is it is of the form:
         *
         *   YYYY-MM-DDThh:mm:ss.s   or  YYYY-MM-DDThh:mm:ss
         *
         * If all fields are not present, this method will return undefiend.
         * Also, if any of the fields cannot be parsed in number form then this
         * method will return undefined. This is not meant to be a generic ISO
         * 8601 parser or all possible formats but is for the strict format and
         * assumptions listed above. The only flexibility this method supports
         * is for the seconds to be an integer or a float.
         */
        if (!str) {
            return;
        }

        var dateTimeFields = str.split('T');
        if (dateTimeFields.length !== 2) {
            return;
        }

        var dateFields = dateTimeFields[0].split('-');
        var timeFields = dateTimeFields[1].split(':');

        if (dateFields.length !== 3 && timeFields.length !== 3) {
            return;
        }

        var year = parseInt(dateFields[0], 10);
        var month = parseInt(dateFields[1], 10);
        var day = parseInt(dateFields[2], 10);

        var hours = parseInt(timeFields[0], 10);
        var minutes = parseInt(timeFields[1], 10);
        var secondsFields = timeFields[2].split('.');
        var seconds = null;
        var milliseconds = null;

        if (secondsFields.length === 1) {
            seconds = parseInt(secondsFields[0], 10);
            milliseconds = 0;
        }
        else if (secondsFields.length === 2) {
            seconds = parseInt(secondsFields[0], 10);
            milliseconds = parseInt(secondsFields[1], 10);
        }

        if (year && month && day && hours && minutes && seconds) {
            /*
             * We subtract one here because the ISO month is in the logical
             * range of [1, 12] as described in the "Calendar dates" section
             * here:
             *
             *       http://en.wikipedia.org/wiki/ISO_8601
             *
             * while the JS Data setUTCMonth() method expects a month in the
             * range of [0, 11] as listed here:
             *
             *       http://www.w3schools.com/jsref/jsref_setutcmonth.asp
             *
             * We need to subtract one to translate the ISO range into the JS
             * range otherwise JS will treat 12 as the first month in the next
             * year.
             */
            var date = new Date();
            date.setUTCFullYear(year);
            date.setUTCMonth(month - 1);
            date.setUTCDate(day);
            date.setUTCHours(hours);
            date.setUTCMinutes(minutes);
            date.setUTCSeconds(seconds, milliseconds);
            return date;
        }

        return;
    };


    var priorityClass = function(priority) {
        var klass;

        switch(priority) {
            case 1:
                klass = 'text-error';
                break;
            case 2:
                klass = 'text-warning';
                break;
            default:
                klass = '';
                break;
        }

        return klass;
    };

    var qualityClass = function(qual) {
        if (qual < 30) {
            return 'text-warning';
        }
        else if (qual >= 50) {
            return 'text-success';
        }
        else {
            return '';
        }
    };


    var samplesInContext = function(context) {
        /*
         * Utility method for retrieving the full list of sample labels in
         * the current context. Given the current sample control, this could
         * be 0, 1, or more sample labels. This method returns a list of the
         * sample labels in the supplied context. If there is an issue
         * retreving them or there are no sample labels, an empty list is
         * returned.
         */
        var samples = [], json;

        if (context && (json = context.get('json'))) {
            _.each(json.children, function(child) {
                if (child.concept && child.concept === 2) {
                    samples = _.pluck(child.value, 'label');
                }
            });
        }

        return samples;
    };


    var toAbsolutePath = function(path) {
        return '' + getRootUrl() + path;
    };


    return {
        depthClass: depthClass,
        effectImpactPriority: effectImpactPriority,
        getRootUrl: getRootUrl,
        groupArticlesByType: groupArticlesByType,
        groupEffectsByType: groupEffectsByType,
        groupPhenotypesByType: groupPhenotypesByType,
        parseISO8601UTC: parseISO8601UTC,
        priorityClass: priorityClass,
        qualityClass: qualityClass,
        samplesInContext: samplesInContext,
        toAbsolutePath: toAbsolutePath
    };

});
