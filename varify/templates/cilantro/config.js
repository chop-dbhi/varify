{% include "cilantro/_config.js" %}
{% load url from future %}

require.paths = {
    'app': '{{ JAVASCRIPT_URL }}',
    'raven': '{{ JAVASCRIPT_URL }}/lib/raven'
};

if (!require.shim) require.shim = {};
require.shim['raven'] = {
    deps: ['jquery'],
    exports: 'Raven'
};

// Explicit default dataview
App.defaults.dataview = {
    columns: [3],
    ordering: [[1, 'asc']]
};

App.root = '{% url "cilantro" %}';

App.alamut_url = '{{ ALAMUT_URL }}';

App.routes = [{
    name: 'app',
    module: 'routes/app',
    route: false
}, {
    name: 'workspace',
    module: 'app/routes/workspace',
    route: '',
    label: 'Workspace'
}, {
    name: 'review',
    module: 'app/routes/review',
    route: 'review/',
    label: 'Review',
    options: {
        perPage: 30
    }
}, {
    name: 'export',
    module: 'app/routes/export',
    route: 'export/',
    label: 'Export',
    options: {
        perPage: 100
    }
}];
