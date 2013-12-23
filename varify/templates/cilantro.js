var csrf_token = '{{ csrf_token }}',

    require = {
        baseUrl: '{{ STATIC_URL }}cilantro/js',
        paths: {
            'project': '{{ JAVASCRIPT_URL }}'
        },
        config: {
            tpl: {
                variable: 'data'
            }
        }
    },

    cilantro = {
        root: '{{ request.META.SCRIPT_NAME }}',
        url: '{% url serrano:root %}',
        main: '#content',
        debug: {% if debug %}true{% else %}false{% endif %}
    };
