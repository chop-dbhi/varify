/* global define */

define([
    'cilantro'
], function(c) {

    var PolyPhenSelector = c.ui.ControlItemView.extend({
        template: 'varify/controls/polyphen',

        ui: {
            select: '.polyphen-selector'
        },

        events: {
            'change .polyphen-selector': 'change'
        },

        initialize: function() {
            this.on('ready', function() {
                /*
                 * Since there is no "empty" option in the list, we need to
                 * call the change method when the control originally renders
                 * so the value is set to the default selected option in the
                 * dropdown and the apply(or update) filter button becomes
                 * activated.
                 */
                return this.change();
            });
        },

        getOperator: function() {
            if (this.ui.select.val() === 'benign') {
                return 'lte';
            }
            else if (this.ui.select.val() === 'possibly-damaging') {
                return 'range';
            }

            return 'gte';
        },

        getValue: function() {
            if (this.ui.select.val() === 'benign') {
                return 0.2;
            }
            else if (this.ui.select.val() === 'possibly-damaging') {
                return [0.2, 0.85];
            }

            return 0.85;
        },

        setOperator: function(operator) {
            if (operator === 'lte') {
                this.ui.select.val('benign');
            }
            else if (operator === 'range') {
                this.ui.select.val('possibly-damaging');
            }
            else {
                this.ui.select.val('probably-damaging');
            }
        }
    });

    return {
        PolyPhenSelector: PolyPhenSelector
    };

});
