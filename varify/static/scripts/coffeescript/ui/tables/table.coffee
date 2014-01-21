define [
    'underscore'
    'marionette'
    './body'
    './header'
], (_, Marionette, body, header) ->


    # Renders a table with one or more tbody elements each representing a
    # frame of data in the collection.
    class ResultTable extends Marionette.CollectionView
        tagName: 'table'

        className: 'table table-striped'

        itemView: body.ResultBody

        itemViewOptions: (item, index) ->
            _.defaults
                collection: item.series
            , @options

        collectionEvents:
            'change:currentpage': 'showCurentPage'

        initialize: ->
            @header = new header.Header

            @$el.append(@header.render().el)

            @collection.on 'reset', =>
                if @collection.objectCount == 0
                    @$el.hide()
                else
                    @$el.show()

        showCurentPage: (model, num, options) ->
            @children.each (view) ->
                view.$el.toggle(view.model.id is num)

    { ResultTable }
