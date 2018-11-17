module.exports = {
    base: '/bocadillo/',
    title: 'Bocadillo',
    description: 'A modern Python web framework filled with asynchronous cheddar',
    lastUpdated: true,
    themeConfig: {
        repo: 'florimondmanca/bocadillo',
        docsBranch: 'docs',
        editLinks: true,
        editLinkText: 'Edit this page on GitHub',
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
                link: 'https://pypi.org/project/bocadillo/',
            },
        ],
        sidebar: [
            '/guide/',
            '/guide/installation',
            '/guide/tutorial',
            {
                title: 'Topics',
                collapsable: false,
                children: [
                    '/guide/topics/async-vs-sync',
                    '/guide/topics/request-handling',
                    '/guide/topics/json',
                    '/guide/topics/templates',
                    '/guide/topics/cli',
                    '/guide/topics/testing',
                    '/guide/topics/deployment',
                ],
            },
            {
                title: 'API Guide',
                collapsable: false,
                children: [
                    '/guide/api-guides/api',
                    '/guide/api-guides/views',
                    '/guide/api-guides/routing',
                    '/guide/api-guides/requests',
                    '/guide/api-guides/responses',
                    '/guide/api-guides/redirecting',
                    '/guide/api-guides/templates',
                    '/guide/api-guides/static-files',
                    '/guide/api-guides/error-handling',
                    '/guide/api-guides/middleware',
                    '/guide/api-guides/cors',
                    '/guide/api-guides/hsts',
                ],
            },
        ],
    },
};
