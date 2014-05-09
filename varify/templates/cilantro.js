var csrf_token = '{{ csrf_token }}',

    require = {
        baseUrl: '{{ STATIC_URL }}cilantro/js',
        paths: {
            'varify': '{{ JAVASCRIPT_URL }}'
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
        phenotype: true,
        debug: {% if debug %}true{% else %}false{% endif %}
    };
