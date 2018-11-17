module.exports = {
    title: 'Bocadillo',
    description: 'A modern Python web framework filled with asynchronous salsa',
    themeConfig: {
        sidebar: [
            {
                title: 'Guide',
                collapsable: false,
                children: [
                    '/api',
                    '/views',
                    '/routing',
                    '/requests',
                    '/responses',
                    '/redirecting',
                    '/templates',
                    '/static-files',
                    '/error-handling',
                    '/middleware',
                    '/cors',
                    '/hsts',
                    '/cli',
                    '/testing',
                    '/deployment',
                ],
            },
        ],
    },
};
