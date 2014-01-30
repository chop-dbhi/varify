define [
    'underscore'
    './models/result'
    './models/assessment'
    './models/phenotype'
], (_, mods...) ->

    _.extend {}, mods...
