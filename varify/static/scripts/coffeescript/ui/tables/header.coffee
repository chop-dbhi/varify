define [
    'underscore'
    'marionette'
    './row'
    'tpl!templates/varify/tables/header.html'
], (_, Marionette, row, templates...) ->

    templates = _.object ['header'], templates

    class Header extends Marionette.ItemView
        tagName: 'thead'

        template: templates.header


    { Header }
