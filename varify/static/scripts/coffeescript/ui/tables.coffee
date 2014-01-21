define [
    'underscore'
    './tables/body'
    './tables/header'
    './tables/row'
    './tables/table'
], (_, mods...) ->

    _.extend {}, mods...
