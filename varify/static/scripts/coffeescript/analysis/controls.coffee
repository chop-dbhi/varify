define [
    'underscore'
    'app/controls'
], (_, Controls) ->

    class OtherOptionControl extends Controls.DataContextNode
        _resetReferences: ->
            super
            @$other = @$('.select-other').hide()
            @$value.on 'change', =>
                if @$value.val() is 'other'
                    @$other.show()
                else
                    @$other.hide()

        change: ->
            if @$value.val() is 'other' and not @$other.val() then return
            super

        setValue: (value) ->
            if @$value.val(value) and not @$value.val()
                @$value.val('other')
                @$('.select-other').val(value).show()
            
        getValue: ->
            if (value = @$value.val()) is 'other'
                value = @$('.select-other').val()
            return @cleanProp value


    class RangeControl extends Controls.DataContextNode
        _resetReferences: ->
            super
            @$value2 = @$('[data-value-2]').hide()

        change: ->
            value1 = @$value.val()
            if @getOperator() is 'range'
                value2 = @cleanProp @$value2.show().val()
                if not value2? or value2 <= value1 then return
            else
                @$value2.hide()
            super

        setValue: (value) ->
            if _.isArray(value)
                @$value.val(value[0])
                @$value2.val(value[1]).show()
            else
                @$value2.val('').hide()
                super value
            return

        getValue: ->
            value1 = super
            if @getOperator() is 'range'
                return [value1, @cleanProp @$value2.val()]
            return value1


    class PercentControl extends OtherOptionControl
        setValue: (value) ->
            if @$value.val(value) and not @$value.val()
                @$value.val('other')
                @$('.select-other').val(value * 100).show()
            
        getValue: ->
            if (value = @$value.val()) is 'other'
                value = @cleanProp(@$('.select-other').val()) / 100.0
            return @cleanProp value

    class CohortAFControl extends Controls.DataContextNode
        setValue: (value) ->
            @$value.val(value * 100)

        getValue: ->
            value = @cleanProp(@$value.val())
            if value then value = value / 100.0
            return value


    class SiftControl extends Controls.DataContextNode
        _getMap: (value) =>
            if value is 'damaging'
                attrs =
                    id: @getId()
                    operator: 'lte'
                    value: 0.5
            else if value is 'tolerated'
                attrs =
                    id: @getId()
                    operator: 'gt'
                    value: 0.5
            else
                attrs = null
            return attrs

        _setMap: (attrs) =>
            if attrs.operator is 'lte'
                return 'damaging'
            else if attrs.operator is 'gt'
                return 'tolerated'

        set: (attrs) ->
            if not attrs then return
            @setValue @_setMap attrs

        get: ->
            return @_getMap(@getValue())


    class PolyPhen2Control extends Controls.DataContextNode
        _getMap: (value) =>
            if value is 'benign'
                attrs =
                    id: @getId()
                    operator: 'lte'
                    value: 0.2
            else if value is 'possibly-damaging'
                attrs =
                    id: @getId()
                    type: 'and'
                    children: [
                        id: @getId()
                        operator: 'gt'
                        value: 0.2
                    ,
                        id: @getId()
                        operator: 'lt'
                        value: 0.85
                    ]
            else if value is 'probably-damaging'
                attrs =
                    id: @getId()
                    operator: 'gte'
                    value: 0.85
            else
                attrs = null
            return attrs

        _setMap: (attrs) =>
            if attrs.type?
                return 'possibly-damaging'
            else if attrs.value is 0.2
                return 'benign'
            else if attrs.value is 0.85
                return 'probably-damaging'

        set: (attrs) ->
            if not attrs then return
            @setValue @_setMap attrs

        get: ->
            return @_getMap(@getValue())


    class TypeaheadControl extends Controls.DataContextNode
        getValue: ->
            typeahead = @$value.data('typeahead')
            if (value = @$value.val())
                values = value.split(typeahead.delimiter)
                if not values[values.length-1]
                    values.pop()
                return values

        setValue: (value) ->
            (typeahead = @$value.data('typeahead')).selections = value
            @$value.val value.join(typeahead.delimiter) + ', '


    { OtherOptionControl, RangeControl, PercentControl, SiftControl, PolyPhen2Control, TypeaheadControl, CohortAFControl }
