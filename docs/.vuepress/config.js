module.exports = {
    base: '/bocadillo/',
    title: 'Bocadillo',
    description: 'A modern Python web framework filled with asynchronous cheddar',
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
            {
                title: 'Usage',
                collapsable: false,
                children: [
                    '/guide/usage/api',
                    '/guide/usage/views',
                    '/guide/usage/routing',
                    '/guide/usage/requests',
                    '/guide/usage/responses',
                    '/guide/usage/redirecting',
                    '/guide/usage/templates',
                    '/guide/usage/static-files',
                    '/guide/usage/error-handling',
                    '/guide/usage/middleware',
                    '/guide/usage/cors',
                    '/guide/usage/hsts',
                    '/guide/usage/cli',
                    '/guide/usage/testing',
                    '/guide/usage/deployment',
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
