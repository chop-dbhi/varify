/* global define */

define([
    'cilantro'
], function(c) {

    /*
     * XXX: I wonder if this could be a mapped range selection control where
     * you can pass in options defining the drop down options and the range
     * that each of them map to. It is fine to use custom controls for now but
     * it is clear from just this Sift control and the PolyPhen control that
     * there will be a need for this type of control going forward so it might
     * be wise to genericize this after Cilantro gains support for passing
     * custom options to controls.
     */
    var SiftSelector = c.ui.ControlItemView.extend({
        template: 'varify/controls/sift',

        ui: {
            select: '.sift-selector'
        },

        events: {
            'change .sift-selector': 'change'
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
                this.change();
            });
        },

        getOperator: function() {
            if (this.ui.select.val() === 'damaging') return 'lte';

            return 'gt';
        },

        getValue: function() {
            return 0.5;
        },

        setOperator: function(operator) {
            if (operator === 'lte') {
                this.ui.select.val('damaging');
            }
            else {
                this.ui.select.val('tolerated');
            }
        }
    });

    return {
        SiftSelector: SiftSelector
    };
});
