define [
    'underscore'
    'marionette'
    './row'
], (_, Marionette, row) ->

    # Represent a "frame" of rows. The model is referenced for keeping
    # track which frame this is relative to the whole series
    class ResultBody extends Marionette.CollectionView
        tagName: 'tbody'

        template: ->

        itemView: row.ResultRow

        itemViewOptions: (model, index) =>
            _.defaults
                resultPk: model.get('pk')
            , @options

    { ResultBody }
