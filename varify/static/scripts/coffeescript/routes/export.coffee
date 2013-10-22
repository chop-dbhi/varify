define [
    'environ'
    'mediator'
    'jquery'
    'underscore'
    'backbone'
    'serrano'
    'routes/review'
], (environ, mediator, $, _, Backbone, Serrano, ReviewArea) ->

    class ExporterButton extends Backbone.View
        template: '
            <div class=btn-group>
                <button class="btn dropdown-toggle" data-toggle=dropdown>Export <span class=caret></span></button>
                <ul class=dropdown-menu></ul>
            </div>
        '

        events:
            'click .dropdown-menu li a': 'export'

        initialize: ->
            @setElement @template

            $.get App.urls.exporter, (resp) =>
                menu = @$('.dropdown-menu')
                for type, link of resp._links
                    if type in ['excel', 'csv']
                        menu.append "<li><a href=\"#{ link.href }\">#{ type.toUpperCase() }</a></li>"

        export: (event) ->
            window.location = $(event.delegateTarget).attr('href')


    class ExportArea extends ReviewArea
        id: 'export-area'

        initialize: ->
            super
            @$toolbar.remove()
            @$toolbar

            @$toolbar = $ '<div class=toolbar />'

            @$toolbar.append '
                <button id=columns-toggle class=btn>Columns...</button>
                <div class=pull-right></div>
            '

            @$toolbar.find('#columns-toggle').on 'click', =>
                @columns.show()

            @$el.prepend @$toolbar

            @exporter = new ExporterButton

            @$toolbar.find('.pull-right').append(@exporter.el)
