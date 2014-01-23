define [
    'underscore'
    'marionette'
    'tpl!templates/varify/tables/header.html'
], (_, Marionette, templates...) ->

    templates = _.object ['header'], templates

    class Header extends Marionette.ItemView
        tagName: 'thead'

        template: templates.header

        initialize: ->
            @data = {}
            if not (@data.view = @options.view)
                throw new Error 'view model required'

    { Header }
