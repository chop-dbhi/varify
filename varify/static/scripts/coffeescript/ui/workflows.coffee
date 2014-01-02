define [
    'underscore'
    './workflows/analysis'
], (_, mods...) ->

    _.extend {}, mods...
