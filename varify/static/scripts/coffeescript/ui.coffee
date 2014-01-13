define [
    'underscore',
    './ui/modals',
    './ui/tables',
    './ui/workflows'
], (_, mods...) ->

    _.extend {}, mods...
