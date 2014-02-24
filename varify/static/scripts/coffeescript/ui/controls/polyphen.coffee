define [
    'underscore'
    'cilantro'
], (_, c) ->

    class PolyPhenSelector extends c.ui.ControlItemView
        template: 'varify/controls/polyphen'

        ui:
            select: '.polyphen-selector'

        events:
            'change .polyphen-selector': 'change'

        initialize: ->
            @on 'ready', ->
                # Since there is no "empty" option in the list, we need to call
                # the change method when the control originally renders so the
                # value is set to the default selected option in the dropdown
                # and the apply(or update) filter button becomes activated.
                @change()

        getOperator: ->
            if @ui.select.val() == 'benign'
                return 'lte'
            else if @ui.select.val() == 'possibly-damaging'
                return 'range'
            else
                return 'gte'

        getValue: ->
            if @ui.select.val() == 'benign'
                return 0.2
            else if @ui.select.val() == 'possibly-damaging'
                return [0.2, 0.85]
            else
                return 0.85

        setOperator: (operator) ->
            if operator == 'lte'
                @ui.select.val('benign')
            else if operator == 'range'
                @ui.select.val('possibly-damaging')
            else
                @ui.select.val('probably-damaging')


    { PolyPhenSelector }
