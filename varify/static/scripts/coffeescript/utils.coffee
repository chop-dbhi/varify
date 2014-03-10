define [], () ->

    parseISO8601UTC = (str) ->
        # This method assumes that the times are expressed in UTC with the
        # special 'Z' designator implied. That is, regardless of whether the
        # string ends in a 'Z' or not, it is assumed that it is in UTC format
        # as discussed in profile definition (1) here:
        #
        #       http://www.w3.org/TR/NOTE-datetime
        #
        # This method as no handling for cases where the times are expressed
        # in local time with a timezone offset. Additionally, this method
        # assumes that the time is complete, that is it is of the form:
        #
        #   YYYY-MM-DDThh:mm:ss.s   or  YYYY-MM-DDThh:mm:ss
        #
        # If all fields are not present, this method will return undefiend.
        # Also, if any of the fields cannot be parsed in number form then this
        # method will return undefined. This is not meant to be a generic ISO
        # 8601 parser or all possible formats but is for the strict format and
        # assumptions listed above. The only flexibility this method supports
        # is for the seconds to be an integer or a float.
        if not str?
            return

        dateTimeFields = str.split('T')

        if dateTimeFields.length != 2
            return

        dateFields = dateTimeFields[0].split('-')
        timeFields = dateTimeFields[1].split(':')

        if dateFields.length != 3 and timeFields.length != 3
            return

        year = parseInt(dateFields[0])
        month = parseInt(dateFields[1])
        day = parseInt(dateFields[2])

        hours = parseInt(timeFields[0])
        minutes = parseInt(timeFields[1])

        secondsFields = timeFields[2].split('.')

        if secondsFields.length == 1
            seconds = parseInt(secondsFields[0])
            milliseconds = 0
        else if secondsFields.length == 2
            seconds = parseInt(secondsFields[0])
            milliseconds = parseInt(secondsFields[1])

        if year and month and day and hours and minutes and seconds
            # We subtract one here because the ISO month is in the logical
            # range of [1, 12] as described in the "Calendar dates" section
            # here:
            #
            #       http://en.wikipedia.org/wiki/ISO_8601
            #
            # while the JS Data setUTCMonth() method expects a month in the
            # range of [0, 11] as listed here:
            #
            #       http://www.w3schools.com/jsref/jsref_setutcmonth.asp
            #
            # We need to subtract one to translate the ISO range into the JS
            # range otherwise JS will treat 12 as the first month in the next
            # year.
            date = new Date();
            date.setUTCFullYear(year)
            date.setUTCMonth(month - 1)
            date.setUTCDate(day)
            date.setUTCHours(hours)
            date.setUTCMinutes(minutes)
            date.setUTCSeconds(seconds, milliseconds)
            return date

        return

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

    { parseISO8601UTC, getRootUrl, toAbsolutePath, effectImpactPriority, priorityClass, depthClass, qualityClass }
