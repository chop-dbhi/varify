/* global define */

define([
    'cilantro',
    'marionette'
], function(c, Marionette) {


    var Frequencies = Marionette.ItemView.extend({
        template: 'varify/variant/frequencies',

        serializeData: function() {
            var data = Marionette.ItemView.prototype.serializeData.apply(
                this, arguments);

            // We need to reference the 1000g value without dot notation to
            // avoid syntax errors due to the key beginning with a number.
            var thousandg = data['1000g'], evs = data.evs;

            // Unless we have a list of one or more elements, just treat the
            // 1000g frequency data as being empty.
            if (thousandg && thousandg.length) {
                thousandg = thousandg[0];

                if (thousandg.all_af) {     // jshint ignore:line
                    thousandg.all_af = c.utils.prettyNumber(thousandg.all_af * 100);    // jshint ignore:line
                }
                if (thousandg.amr_af) {     // jshint ignore:line
                    thousandg.amr_af = c.utils.prettyNumber(thousandg.amr_af * 100);    // jshint ignore:line
                }
                if (thousandg.afr_af) {     // jshint ignore:line
                    thousandg.afr_af = c.utils.prettyNumber(thousandg.afr_af * 100);    // jshint ignore:line
                }
                if (thousandg.eur_af) {     // jshint ignore:line
                    thousandg.eur_af = c.utils.prettyNumber(thousandg.eur_af * 100);    // jshint ignore:line
                }

                data.thousandg = thousandg;
            }
            else {
                data.thousandg = null;
            }

            // Unless we have a list of one or more elements, just treat the
            // evs frequency data as being empty.
            if (evs && evs.length) {
                evs = evs[0];

                if (evs.all_af) {   // jshint ignore:line
                    evs.all_af = c.utils.prettyNumber(evs.all_af * 100);    // jshint ignore:line
                }
                if (evs.afr_af) {   // jshint ignore:line
                    evs.afr_af = c.utils.prettyNumber(evs.afr_af * 100);    // jshint ignore:line
                }
                if (evs.eur_af) {   // jshint ignore:line
                    evs.eur_af = c.utils.prettyNumber(evs.eur_af * 100);    // jshint ignore:line
                }

                data.evs = evs;
            }
            else {
                data.evs = null;
            }

            return data;
        }
    });

    return {
        Frequencies: Frequencies
    };

});
