define [
    'underscore'
    'marionette'
], (_, Marionette) ->

    class Header extends Marionette.ItemView
        tagName: 'thead'

        template: 'varify/tables/header'

        events:
            'click th': 'onClick'

        initialize: ->
            @data = {}
            if not (@data.view = @options.view)
                throw new Error 'view model required'

        _getConcept: (element) ->
            concept = parseInt(element.getAttribute('data-concept-id'))

            if concept? and not isNaN(concept)
                return concept

            # It is possible we registered a click event on a child of the
            # th element. If that is the case, try to read the concept from
            # parent of the event target.
            return parseInt(element.parentElement.getAttribute('data-concept-id'))

        onClick: (event) =>
            concept = @_getConcept(event.target)

            if not concept? or isNaN(concept)
                throw new Error 'Unrecognized concept ID on column'

            model = _.find @data.view.facets.models, (f) ->
                return f.get('concept') == concept

            # If this column is not in the view already, add it in before
            # updating the view sort properties.
            if not model?
                @data.view.facets.add({concept: concept})

            _.each @data.view.facets.models, (f) ->
                if f.get('concept') == concept
                    direction = f.get('sort')

                    if direction?
                        if direction.toLowerCase() == "asc"
                            f.set('sort', "desc")
                            f.set('sort_index', 0)
                        else
                            f.unset('sort')
                            f.unset('sort_index')
                    else
                        f.set('sort', "asc")
                        f.set('sort_index', 0)
                else
                    f.unset('sort')
                    f.unset('sort_index')

            @data.view.save()

        onRender: =>
            _.each @data.view.facets.models, (f) ->
                $sortIcon = $("th[data-concept-id=#{ f.get('concept') }] i")

                if $sortIcon?
                    $sortIcon.removeClass('icon-sort icon-sort-up icon-sort-down')

                    direction = (f.get('sort') or '').toLowerCase()

                    sortClass = switch direction
                        when 'asc' then 'icon-sort-up'
                        when 'desc' then 'icon-sort-down'
                        else 'icon-sort'

                    $sortIcon.addClass(sortClass)

    { Header }
