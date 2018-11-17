module.exports = {
    base: '/bocadillo/',
    title: 'Bocadillo',
    description: 'A modern Python web framework filled with asynchronous cheddar',
    themeConfig: {
        nav: [
            {
                text: 'Home',
                link: '/',
            },
            {
                text: 'Guide',
                link: '/guide/',
            },
            {
                text: 'Changelog',
                link: 'https://github.com/florimondmanca/bocadillo/blob/master/CHANGELOG.md',
            },
            {
                text: 'PyPI',
                link: 'https://pypi.org/project/bocadillo',
            },
            {
                text: 'GitHub',
                link: 'https://github.com/florimondmanca/bocadillo',
            },
        ],
        sidebar: [
            {
                title: 'Guide',
                collapsable: false,
                children: [
                    '/guide/',
                    '/guide/api',
                    '/guide/views',
                    '/guide/routing',
                    '/guide/requests',
                    '/guide/responses',
                    '/guide/redirecting',
                    '/guide/templates',
                    '/guide/static-files',
                    '/guide/error-handling',
                    '/guide/middleware',
                    '/guide/cors',
                    '/guide/hsts',
                    '/guide/cli',
                    '/guide/testing',
                    '/guide/deployment',
                ],
            },
        ],
    },
    markdown: {
        toc: {
            includeLevel: [1, 2],
        },
    },
};
