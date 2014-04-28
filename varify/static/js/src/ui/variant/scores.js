/* global define */

define([
    'marionette'
], function(Marionette) {

    var PredictionScores = Marionette.ItemView.extend({
        template: 'varify/variant/scores',

        getPrediction: function(score) {
            var prediction;

            if (score in this.model.attributes && this.model.get(score).length) {
                prediction = this.model.get(score)[0].prediction;
            }

            return prediction;
        },

        templateHelpers: function() {
            var sift = this.getPrediction('sift'),
                siftClass = '',
                polyphen = this.getPrediction('polyphen2'),
                polyphenClass = '';

            switch (sift) {
                case 'Damaging':
                    siftClass = 'text-error';
                    break;
                default:
                    siftClass = 'muted';
            }

            switch (polyphen) {
                case 'Probably Damaging':
                    polyphenClass = 'text-error';
                    break;
                case 'Possibly Damaging':
                    polyphenClass = 'text-warning';
                    break;
                default:
                    polyphenClass = 'muted';
            }

            return {
                siftClass: siftClass,
                polyphenClass: polyphenClass
            };
        },

        serializeData: function() {
            var data = Marionette.ItemView.prototype.serializeData.apply(
                this, arguments);

            data.sift = this.getPrediction('sift');
            data.polyphen = this.getPrediction('polyphen2');

            return data;
        }
    });

    return {
        PredictionScores: PredictionScores
    };
});
