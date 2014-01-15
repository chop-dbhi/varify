define [
    'underscore'
    './models/result'
    './models/assessment'
], (_, mods...) ->

    _.extend {}, mods...
