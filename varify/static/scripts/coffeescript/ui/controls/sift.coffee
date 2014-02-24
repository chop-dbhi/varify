define [
    'underscore'
    'cilantro'
], (_, c) ->

    # XXX: I wonder if this could be a mapped range selection control where you
    # can pass in options defining the drop down options and the range that
    # each of them map to. It is fine to use custom controls for now but it is
    # clear from just this Sift control and the PolyPhen control that there
    # will be a need for this type of control going forward so it might be
    # wise to genericize this after Cilantro gains support for passing custom
    # options to controls.
    class SiftSelector extends c.ui.ControlItemView
        template: 'varify/controls/sift'

        ui:
            select: '.sift-selector'

        events:
            'change .sift-selector': 'change'

        initialize: ->
            @on 'ready', ->
                # Since there is no "empty" option in the list, we need to call
                # the change method when the control originally renders so the
                # value is set to the default selected option in the dropdown
                # and the apply(or update) filter button becomes activated.
                @change()

        getOperator: ->
            if @ui.select.val() == 'damaging'
                return 'lte'
            else
                return 'gt'

        getValue: ->
            return 0.5

        setOperator: (operator) ->
            if operator == 'lte'
                @ui.select.val('damaging')
            else
                @ui.select.val('tolerated')


    {SiftSelector}
