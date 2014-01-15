define [
    'underscore'
    './workflows/results'
], (_, mods...) ->

    _.extend {}, mods...
