define [
    'environ'
    'mediator'
    'jquery'
    'underscore'
    'backbone'
    'serrano'
], (environ, mediator, $, _, Backbone, Serrano) ->

    # Encapsulates a group of control elements that represents a
    # DataContextNode, i.e. a single condition or branch of nodes. When
    # the data is ready to be saved, the view will utilize various methods
    # extract and populate the DataContextNode model instance.
    # ---
    # A node property can be represented as a static value via an attribute
    # (e.g. data-id="39") or as a dynamic value via a form element.
    class DataContextNode extends Backbone.View
        idSelector: '[data-id]'
        valueSelector: '[data-value]'
        operatorSelector: '[data-operator]'

        # Attribute-based properties representing a constant value
        idAttr: 'data-id'
        valueAttr: 'data-value'
        operatorAttr: 'data-operator'

        events:
            'click input[type=radio],input[type=checkbox]': 'change'
            'change select': 'change'
            'blur input': 'change'

        initialize: (options={}) ->
            # Custom selectors
            @idSelector = options.idSelector or @idSelector
            @valueSelector = options.valueSelector or @valueSelector
            @operatorSelector = options.operatorSelector or @operatorSelector

            # Custom attributes
            @idAttr = options.idAttr or @idAttr
            @valueAttr = options.valueAttr or @valueAttr
            @operatorAttr = options.operatorAttr or @operatorAttr

            @_resetReferences()

            # Populate the attributes
            if @model
                @on 'change', (view, attrs) ->
                    if attrs
                        @model.id = attrs.id
                        @model.set attrs
                        mediator.publish Serrano.DATACONTEXT_ADD, @model
                    else
                        @model.clear()
                        mediator.publish Serrano.DATACONTEXT_REMOVE, @model

                # Load existing data, otherwise trigger a change in case
                # there are default values
                if @model.id
                    @set @model.attributes
                else
                    @change()
        
        # Call this if the underlying DOM elements change
        _resetReferences: ->
            @$id = if @$el.is @idSelector then @$el else @$ @idSelector
            @$operator = if @$el.is @operatorSelector then @$el else @$ @operatorSelector
            @$value = if @$el.is @valueSelector then @$el else @$ @valueSelector

        cleanProp: (value) ->
            # Attempt to coerce to a more native type
            if _.isString value
                if value.toLowerCase() is 'null'
                    return null
                if value.toLowerCase() is 'true'
                    return true
                if value.toLowerCase() is 'false'
                    return false
                if not _.isNaN parseFloat(value)
                    return parseFloat(value)
                if value is '' then return
            return value

        getId: ->
            el = @$id
            @cleanProp if el.is 'input,select' then el.val() else el.attr @idAttr

        getOperator: ->
            el = @$operator
            @cleanProp if el.is 'input,select' then el.val() else el.attr @operatorAttr

        getValue: ->
            el = @$value
            if el.is 'select[multiple]'
                _.map el.val(), @cleanProp
            else if el.is '[type=checkbox]'
                if el.length > 1
                    _.map el, (e) -> @cleanProp $(e).val()
                else
                    @cleanProp el.val()
            else if el.is 'input,select'
                # If this is already null or undefined, treat as empty
                # rather than an explicit null value via 'null'
                if not (value = el.val())? then return
                @cleanProp el.val()
            else
                @cleanProp el.attr @valueAttr

        setId: (id) ->
            if not id? then return
            el = @$id
            if el.is 'input,select' then el.val(id) else el.attr(@idAttr, id)
            return

        setOperator: (operator) ->
            el = @$operator
            if el.is 'input,select' then el.val(operator) else el.attr(@operatorAttr, operator)
            return

        setValue: (value) ->
            el = @$value
            if value? then value = value.toString()
            if el.is 'input,select' then el.val(value) else el.attr(@valueAttr, value)
            return

        change: ->
            @trigger 'change', @, @get()

        get: ->
            if (value = @getValue()) is undefined or (_.isArray(value) and value[0] is undefined)
                attrs = null
            else
                attrs =
                    id: @getId()
                    operator: @getOperator()
                    value: value
            return attrs

        set: (attrs) ->
            if attrs.value isnt undefined
                @setId attrs.id
                @setValue attrs.value
                @setOperator attrs.operator


    { DataContextNode }
