define [
    'environ'
    'mediator'
    'jquery'
    'underscore'
    'backbone'
    'serrano',
    'app/review/views'
    'app/review/models'
    'views/columns'
], (environ, mediator, $, _, Backbone, Serrano, Views, Models, Columns) ->


    class DataRows extends Backbone.View
        tagName: 'table'
        
        id: 'variant-table'
                
        render: -> @$el


    class Sorter extends Columns
        template: _.template '
            <div id=columns-modal class="modal fade">
                <div class=modal-header>
                    <a class=close data-dismiss=modal>×</a>
                    <h3>Sort Options</h3>
                </div>
                <div class=modal-body>
                    <ul class="available-columns span5"></ul>
                    <ul class="selected-columns span5"></ul>
                </div>
                <div class=modal-footer>
                    <button data-save class="btn btn-primary">Save</button>
                    <button data-close class=btn>Close</button>
                </div>
            </div>
        '

        selectedItemTemplate: _.template '
            <li data-id={{ id }}>
                <select>
                    <option value="asc" title="ascending">Asc</option>
                    <option value="desc" title="descending">Desc</option>
                </select>
                {{ name }}
                <span class=controls>
                    <button class="btn btn-danger btn-mini">-</button>
                </span>
            </li>
        '
        initialize: ->
            # Skip the Columns class to prevent the subscription
            Columns.__super__.initialize.apply @, arguments

            @setElement @template()

            @$available = @$ '.available-columns'
            @$selected = @$('.selected-columns').sortable
                cursor: 'move'
                forcePlaceholderSize: true
                placeholder: 'placeholder'

            @$el.addClass 'loading'
            @collection.when =>
                @$el.removeClass 'loading'
                @render()
                @resolve()

            mediator.subscribe Serrano.DATAVIEW_SYNCED, (model) =>
                if model.isSession() and (json = model.get('json'))
                    @add id, dir for [id, dir] in json.ordering
                return

        add: (id, dir) =>
            # Set the direction
            (super).find('select').val(dir)

        render: =>
            availableHtml = []
            selectedHtml = []

            for model in @collection.filter((model) -> model.get('sortable'))
                availableHtml.push @availableItemTemplate model.attributes
                selectedHtml.push @selectedItemTemplate model.attributes

            @$available.html availableHtml.join ''
            @$selected.html selectedHtml.join ''
            return @

        save: ->
            @hide()
            ordering = _.map @$selected.children(), (elem) ->
                if (data = $(elem).data()).selected and data.id
                    return [data.id, $('select', elem).val()]

            mediator.publish Serrano.DATAVIEW_ORDERING, _.filter(ordering, (x) -> x?)


    class ReviewArea extends Backbone.View
        el: '#review-area'

        events:
            'click .variant-container': 'checkForAlamut'

        deferred:
            loadData: true

        initialize: ->
            super

            # When the user clicks a variant summary, we need to show the
            # modal window for details and knowledge capture
            mediator.subscribe 'review/summary/click', (summaryView, resultView) => 
                @reviewModal.update(summaryView, resultView)

            @reviewModal = new Views.ReviewModal

            # When the analysis is being edited, the results should not update
            # since multiple changes to the analysis may be occuring.
            mediator.subscribe 'analysis/editing/start', =>
                @pending()

            # Special handling since this view may or may not be in view
            mediator.subscribe 'analysis/editing/done', =>
                if @loaded then @resolve()

            mediator.subscribe Serrano.DATACONTEXT_SYNCED, =>
                @loadData()

            mediator.subscribe Serrano.DATAVIEW_SYNCED, (model) =>
                @loadData()

                if not (json = model.get('json')) or not json.ordering?
                    return
                App.DataConcept.when =>
                    html = []
                    for [id, dir] in model.get('json').ordering
                        html.push "#{ App.DataConcept.get(id).get('name') } (#{ dir })"
                    if not html.length
                        html.push '<span class=muted>No sorting applied.</span>'
                    @$toolbar.find('#ordering-text').html(html.join(', '))

            @$toolbar = $ '<div class=toolbar />'

            @$toolbar.append '
                <button id=sorter-toggle class=btn>Sort...</button>
                <span id=ordering-text></span>
            '

            @$el.append @$toolbar

            notification = $ '<div id=review-notification class="alert hide" />'
            @$el.append notification

            @sorter = new Sorter
                collection: App.DataConcept

            @$toolbar.find('#sorter-toggle').on 'click', (event) =>
                @sorter.show()

            @sorter.$el.appendTo('body')

            @dataRows = new DataRows
            @$el.append @dataRows.render()

            @$el.scroller
                autofill: true
                container: '#main-area .inner'
                trigger: => @loadData true

            @page_num = 1
            @num_pages = null

        checkForAlamut: ->
            if !(@hasCheckedForAlamut?)
                $.ajax({
                    url:  App.alamut_url + '/version',
                    datatype: 'xml',
                    error: () ->
                        $('.alamut-button').removeClass('btn-primary')
                        $('.alamut-button').addClass('disabled')
                        $('.alamut-button').attr('href', '#')
                        $('.alamut-button').parent().append('<p class=text-warning>The query feature has been disabled because no Alamut instance was found.</p>')
                })

            @hasCheckedForAlamut = true

        load: ->
            @$el.show()
            @$toolbar.show()
            @resolve()
            @loaded = true

        unload: ->
            @$el.hide()
            @$toolbar.hide()
            @loaded = false
        
        # Verifies that the current sessions DataContext is defined and has a
        # valid proband(sample) defined within its nodes.
        isCurrentContextValid: ->
            # Don't try to load data if we don't have a valid context
            currentContext = App.DataContext.getSession()

            if not currentContext?
                return false

            # Do not let requests hit the server if no proband is selected.
            nodes = currentContext.nodes

            if not nodes?
                return false
            
            # 2 is the ID of the sample nodes. It's set in L37 of:
            #   varify/templates/analysis/_proband.html
            sampleNodeArray = nodes[2]

            if not sampleNodeArray or sampleNodeArray.length < 1
                return false

            sampleNode = sampleNodeArray[0]
            attrs = sampleNode.attributes

            if not attrs? or not attrs.value?
                return false
            
            return true

        loadData: (append=false) =>
            if not @isCurrentContextValid()
                return
            
            # If appending data, ensure the last page has not already been loaded
            if append and @page_num is @num_pages then return

            url = "#{ App.urls.preview }?per_page=#{ @options.perPage }"

            if append
                url = "#{ url }&page=#{ ++@page_num }"
            else
                @page_num = 1
                @$el.addClass 'loading'

            # This is hideous, but is suitable for now..
            App.DataView.when =>
                # The representation of the DataView must be fixed for this view since
                # only the Result ID is needed. The current DataView session
                # is used purely for the ordering
                json = _.clone App.DataView.getSession().get('json')
                json.columns = App.defaults.dataview.columns

                Backbone.ajax
                    url: url
                    type: 'post'
                    contentType: 'application/json'
                    dataType: 'json'
                    data: JSON.stringify(view: json)
                    success: (resp) =>
                        @page_num = resp.page_num
                        @num_pages = resp.num_pages
                        @updatePage resp.objects, append

                    complete: =>
                        @$el.removeClass 'loading'
            return

        updatePage: (objects, append) ->
            if not append then @dataRows.$el.empty()
            for obj in objects
                @loadRow obj.pk, parseInt obj.values[0]
            @$el.scroller 'reset'
            
            return

        # A row is composed of a result and a variant
        loadRow: (id, variantId) ->
            result = new Models.ResultVariant
                id: id

            resultView = new Views.Result
                model: result

            variantView = new Views.VariantSummary
                model: result
                resultView: resultView
                variantId: variantId

            result.fetch()

            # This need to happen here to ensure the order of the results is
            # maintained
            @dataRows.$el.append variantView.el
