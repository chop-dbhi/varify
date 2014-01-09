define [
    'underscore'
    'marionette'
    './body'
], (_, Marionette, body) ->


    # Renders a table with one or more tbody elements each representing a
    # frame of data in the collection.
    class ResultTable extends Marionette.CollectionView
        tagName: 'table'

        className: 'table table-striped'

        itemView: body.ResultBody

        itemViewOptions: (item, index) ->
            _.defaults
                collection: item.series
                rootUrl: @data.rootUrl
            , @options

        collectionEvents:
            'change:currentpage': 'showCurentPage'

        initialize: ->
            @data = {}
            if not (@data.rootUrl = @options.rootUrl)
                throw new Error 'root url required'

            @collection.on 'reset', =>
                if @collection.objectCount == 0
                    @$el.hide()
                else
                    @$el.show()

        showCurentPage: (model, num, options) ->
            @children.each (view) ->
                view.$el.toggle(view.model.id is num)

    { ResultTable }
