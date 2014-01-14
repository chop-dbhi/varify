define [], () ->

    getRootUrl = () ->
        # Get the route-free URL. That is, we want to remove the route at the
        # end of the URL and be left with the root URL so we can use this to
        # construct the result URLs later on.
        window.location.href.replace(new RegExp('/[^/]*/$'), '/')

    toAbsolutePath = (path) ->
        return "#{ getRootUrl() }#{ path }"

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

    { getRootUrl, toAbsolutePath, effectImpactPriority, priorityClass, depthClass, qualityClass }
