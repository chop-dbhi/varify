define [
    'underscore'
    './tables/body'
    './tables/row'
    './tables/table'
], (_, mods...) ->

    _.extend {}, mods...
