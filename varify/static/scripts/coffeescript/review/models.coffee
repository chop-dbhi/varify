define [
    'environ'
    'underscore'
    'backbone'
    '../utils'
], (environ, _, Backbone, utils) ->

    class Assessment extends Backbone.Model
        urlRoot: ->
            environ.absolutePath "/api/assessments/"

        defaults:
            'evidence_details': ''
            'sanger_requested': 'undefined'
            'assessment_category': 'undefined'
            'father_result': 'undefined'
            'mother_result': 'undefined'
            'pathogenicity': 1
            'created': 'undefined'
            'modified': 'undefined'
            'sample_result': 'undefined'
        
        parse: (response) ->
            if response?
                data = response
            
                objFields = ['assessment_category', 'father_result', 'mother_result', 'pathogenicity']
                
                _.each objFields, (field) ->
                    if response[field]
                        data[field] = (response[field])['id']

                return data

    class AssessmentMetrics extends Backbone.Model
        url: -> environ.absolutePath "/api/variants/#{ @variant_id }/assessment-metrics/"

        initialize: (attrs, options) ->
            @sample_result = options.sample_result
            @variant_id = options.variant_id

    class ResultVariant extends Backbone.Model
        url: ->
            environ.absolutePath "/api/samples/variants/#{ @id }/"

        parse: (attrs) ->
            variant = attrs.variant


            # Bit of a hacked use of sortBy..
            variant.effects = _.sortBy variant.effects, (eff) ->
                utils.effectImpactPriority eff.impact

            uniqueGenes = {}
            genes = []

            _.each variant.effects, (eff) ->
                if not eff.transcript or not (gene = eff.transcript.gene)
                    return

                if /^LOC\d+/.test(gene.symbol) or uniqueGenes[gene.symbol]?
                    return

                uniqueGenes[gene.symbol] = true
                genes.push
                    symbol: gene.symbol
                    hgnc_id: gene.hgnc_id
                    name: gene.name

            variant.uniqueGenes = genes

            return attrs


    # Paginated resource that will update the collection. It assumes
    # the response has `num_pages` and `page_num` properties.
    class PaginatedResource extends Backbone.Collection
        initialize: ->
            super

            @pageNum = 0
            @numPages = null

        parse: (resp) ->
            @numPages = resp.num_pages
            @pageNum = resp.page_num
            return resp.results

        hasNext: -> @pageNum isnt @num_pages

        next: ->
            if @hasNext()
                @fetch
                    add: true
                    data: page_num: ++@pageNum



    { Assessment, AssessmentMetrics, ResultVariant, PaginatedResource }
