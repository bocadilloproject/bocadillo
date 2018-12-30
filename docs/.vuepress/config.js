const listDir = require('./utils').listDir;

if (process.env.NODE_ENV !== 'production') {
    require('dotenv').load();
}

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
    serviceWorker: true,
    themeConfig: {
        repo: 'bocadilloproject/bocadillo',
        docsDir: 'docs',
        docsBranch: 'release/docs',
        editLinks: true,
        editLinkText: 'Edit this page on GitHub',
        sidebarDepth: 2,
        lastUpdated: true,
        serviceWorker: {updatePopup: true},
        algolia: {
            apiKey: process.env.ALGOLIA_API_KEY,
            indexName: "bocadilloproject",
        },
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
                text: 'How-To',
                link: '/how-to/',
            },
            {
                text: 'API Reference',
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
                    children: listDir('getting-started', [
                        '',
                        'installation',
                        'quickstart',
                    ]),
                },
            ],
            '/topics/': [
                '/topics/api',
                {
                    title: 'HTTP',
                    collapsable: false,
                    children: listDir('topics/http', [
                        'routes-url-design',
                        'views',
                        'requests',
                        'responses',
                        'redirecting',
                        'media',
                        'static-files',
                        'hooks',
                        'background-tasks',
                        'middleware',
                    ]),
                },
                {
                    title: 'Protocol-agnostic',
                    collapsable: false,
                    children: listDir('topics/agnostic', [
                        'templates',
                        'recipes',
                        'events',
                    ]),
                },
                {
                    title: 'Tooling',
                    collapsable: false,
                    children: listDir('topics/tooling', [
                        'cli',
                    ]),
                },
                {
                    title: 'Discussions',
                    collapsable: false,
                    children: listDir('topics/discussions', [
                        'async-vs-sync',
                        'deployment',
                        'security',
                    ])
                }
            ],
            '/how-to/': [
                {
                    title: 'How-To',
                    collapsable: false,
                    children: listDir('how-to', [
                        'custom-cli-commands',
                        'extra-media-handlers',
                        'middleware',
                    ]),
                },
            ],
            '/api/': [
                {
                    title: 'Python modules',
                    collapsable: false,
                    children: listDir('api').map(child => {
                        const filename = child.split('/')[2];
                        const displayName = filename.replace('.md', '.py');
                        return [child, displayName];
                    }),
                },
            ],
        },
    },
};
