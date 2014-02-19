define [
    'underscore'
    './controls/hgmd'
    './controls/sift'
    './controls/polyphen'
], (_, mods...) ->

    _.extend {}, mods...
