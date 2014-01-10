define [
    'underscore'
    './tables/body'
    './tables/cell'
    './tables/row'
    './tables/table'
], (_, mods...) ->

    _.extend {}, mods...
