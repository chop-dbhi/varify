define [
    'underscore'
    './controls/sift'
    './controls/polyphen'
], (_, mods...) ->

    _.extend {}, mods...
