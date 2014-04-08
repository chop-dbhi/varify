({
    appDir: 'src',
    baseUrl: '.',
    dir: 'min',
    inlineText: true,
    preserveLicenseComments: false,
    generateSourceMaps: true,
    wrap: false,
    logLevel: 1,

    throwWhen: {
        optimize: true
    },

    // RequireJS plugin configs
    config: {
        tpl: {
            variable: 'data'
        }
    },

    paths: {
        'jquery': 'empty:',
        'cilantro': 'empty:',
        'underscore': 'empty:',
        'backbone': 'empty:',
        'marionette': 'empty'
    },

    modules: []
})
