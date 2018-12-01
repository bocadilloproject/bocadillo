module.exports = {
    base: '/',
    title: 'Bocadillo',
    description: 'A modern Python web framework filled with asynchronous salsa',
    lastUpdated: true,
    head: [
        // Twitter card meta tags
        ['meta', {name: 'twitter:card', content: 'summary'}],
        ['meta', {
            name: 'twitter:url',
            content: 'https://bocadillo.github.io'
        }],
        ['meta', {name: 'twitter:site', content: 'Bocadillo'}],
        ['meta', {name: 'twitter:creator', content: 'Florimond Manca'}],
        ['meta', {name: 'twitter:title', content: 'Bocadillo'}],
        ['meta', {
            name: 'twitter:description',
            content: 'A modern Python web framework filled with asynchronous salsa'
        }],
        ['meta', {
            name: 'twitter:image',
            content: 'https://bocadilloproject.github.io/social-image.png'
        }],
    ],
    themeConfig: {
        repo: 'bocadilloproject/bocadillo',
        docsDir: 'docs',
        docsBranch: 'release/docs',
        editLinks: true,
        editLinkText: 'Edit this page on GitHub',
        nav: [
            {
                text: 'Home',
                link: '/',
            },
            {
                text: 'Get Started',
                link: '/getting-started/',
            },
            {
                text: 'Topics',
                link: '/topics/',
            },
            {
                text: 'How To',
                link: '/how-to/',
            },
            {
                text: 'API',
                link: '/api/',
            },
            {
                text: 'Changelog',
                link: 'https://github.com/bocadilloproject/bocadillo/blob/master/CHANGELOG.md',
            },
            {
                text: 'PyPI',
                link: 'https://pypi.org/project/bocadillo/',
            },
        ],
        sidebar: {
            '/getting-started/': [
                {
                    title: 'Getting Started',
                    collapsable: false,
                    children: [
                        '/getting-started/',
                        '/getting-started/installation',
                        '/getting-started/tutorial',
                        '/getting-started/next-steps',
                    ],
                },
            ],
            '/topics/': [
                {
                    title: 'Handling HTTP requests',
                    collapsable: false,
                    children: [
                        '/topics/request-handling/routes-url-design',
                        '/topics/request-handling/writing-views',
                        '/topics/request-handling/redirecting',
                        '/topics/request-handling/hooks',
                        '/topics/request-handling/media',
                    ]
                },
                {
                    title: 'Common functionality',
                    collapsable: false,
                    children: [
                        '/topics/common/templates',
                        '/topics/common/static-files',
                        '/topics/common/cors',
                        '/topics/common/hsts',
                        '/topics/common/middleware',
                    ],
                },
                {
                    title: 'Beyond development',
                    collapsable: false,
                    children: [
                        '/topics/testing',
                        '/topics/deployment',
                    ],
                },
                {
                    title: 'Discussions',
                    collapsable: false,
                    children: [
                        '/topics/async-vs-sync',
                    ]
                }
            ],
            '/how-to/': [
                {
                    title: 'How To',
                    collapsable: false,
                    children: [
                        '/how-to/custom-cli-commands',
                        '/how-to/extra-media-handlers',
                        '/how-to/routing-middleware',
                    ],
                },
            ],
            '/api/': [
                {
                    title: 'API Reference',
                    collapsable: false,
                    children: [],
                },
            ],
        },
    },
};
