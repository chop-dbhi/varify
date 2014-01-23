define [
    'underscore'
    'marionette'
    'tpl!templates/varify/tables/header.html'
], (_, Marionette, templates...) ->

    templates = _.object ['header'], templates

    class Header extends Marionette.ItemView
        tagName: 'thead'

        template: templates.header

        events:
            'click th': 'onClick'

        initialize: ->
            @data = {}
            if not (@data.view = @options.view)
                throw new Error 'view model required'

        onClick: (event) =>
            concept = parseInt(event.target.getAttribute('data-concept-id'))

            if not concept?
                throw new Error 'Unrecognized concept ID on column'

            model = _.find @data.view.facets.models, (f) ->
                return f.get('concept') == concept

            # If this column is not in the view already, add it in before
            # updating the view sort properties.
            if not model?
                @data.view.facets.add({concept: concept})

            console.log("Clicked #{ concept }")
            _.each @data.view.facets.models, (f) ->
                console.log("Comparing against #{ f.get('concept') }")
                if f.get('concept') == concept
                    direction = f.get('sort')

                    if direction?
                        if direction.toLowerCase() == "asc"
                            console.log("asc --> desc")
                            f.set('sort', "desc")
                            f.set('sort_index', 0)
                        else
                            console.log("desc --> none")
                            f.unset('sort')
                            f.unset('sort_index')
                    else
                        console.log("none --> asc")
                        f.set('sort', "asc")
                        f.set('sort_index', 0)
                else
                    console.log("no click match, unsetting")
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
