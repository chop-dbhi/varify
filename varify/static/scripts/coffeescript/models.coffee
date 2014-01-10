define [
    'underscore'
    './models/result'
], (_, mods...) ->

    _.extend {}, mods...
