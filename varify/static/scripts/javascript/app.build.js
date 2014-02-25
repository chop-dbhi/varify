({
    appDir: 'src',
    baseUrl: '.',
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

    dir: 'min',

    modules: []
})
