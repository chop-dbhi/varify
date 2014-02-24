define [
    'underscore'
    'cilantro'
], (_, c) ->

    # XXX: This should be a isnull selector generic control in Cilantro. Until
    # Cilantro supports custom options for controls, we will continue to use
    # this custom control as we need to dictate the labels on the options in
    # the dropdown.
    class HgmdSelector extends c.ui.ControlItemView
        template: 'varify/controls/hgmd'

        ui:
            select: '.hgmd-selector'

        events:
            'change .hgmd-selector': 'change'

        initialize: ->
            @on 'ready', ->
                # Since there are only 2 options in the list, we need to call
                # the change method when the control originally renders so the
                # value is set to the default selected option in the dropdown
                # and the apply(or update) filter button becomes activated.
                @change()

        getOperator: ->
            return "isnull"

        getValue: ->
            # The isnull operator is only compatible with boolean values so we
            # need to return a boolean as a value here instead of the string
            # value of the dropdown.
            return @ui.select.val() == "true"

        setValue: (value) ->
            # The value will be a boolean so we need to convert it to a string
            # in order for it to be recognized in the val() setter on the
            # dropdown.
            @ui.select.val(value.toString())


    { HgmdSelector }
