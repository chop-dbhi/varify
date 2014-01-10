define [], () ->

    effectImpactPriority = (impact) ->
        switch impact
            when 'High' then 1
            when 'Moderate' then 2
            when 'Low' then 3
            when 'Modifier' then 4
            else 5


    priorityClass = (priority) ->
        switch priority
            when 1 then 'text-error'
            when 2 then 'text-warning'
            else ''

    depthClass = (depth) ->
        if depth < 10
            'text-warning'
        else if depth >= 30
            'text-success'
        else
            ''

    qualityClass = (qual) ->
        if qual < 30
            'text-warning'
        else if qual >= 50
            'text-success'
        else
            ''

    { effectImpactPriority, priorityClass, depthClass, qualityClass }
