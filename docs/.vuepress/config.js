const listDir = require("./utils").listDir;

require("dotenv").load();

module.exports = {
  base: "/",
  title: "Bocadillo",
  description: "A modern Python web framework filled with asynchronous salsa",
  lastUpdated: true,
  head: [
    // Twitter card meta tags
    ["meta", { name: "twitter:card", content: "summary" }],
    [
      "meta",
      {
        name: "twitter:url",
        content: "https://bocadillo.github.io"
      }
    ],
    ["meta", { name: "twitter:site", content: "Bocadillo" }],
    ["meta", { name: "twitter:creator", content: "Florimond Manca" }],
    ["meta", { name: "twitter:title", content: "Bocadillo" }],
    [
      "meta",
      {
        name: "twitter:description",
        content: "A modern Python web framework filled with asynchronous salsa"
      }
    ],
    [
      "meta",
      {
        name: "twitter:image",
        content: "https://bocadilloproject.github.io/social-image.png"
      }
    ]
  ],
  serviceWorker: true,
  themeConfig: {
    repo: "bocadilloproject/bocadillo",
    docsDir: "docs",
    docsBranch: "release/docs",
    editLinks: true,
    editLinkText: "Edit this page on GitHub",
    sidebarDepth: 2,
    lastUpdated: true,
    serviceWorker: { updatePopup: true },
    algolia:
      process.env.NODE_ENV === "production"
        ? {
            apiKey: process.env.ALGOLIA_API_KEY,
            indexName: "bocadilloproject"
          }
        : {},
    nav: [
      {
        text: "Get Started",
        link: "/getting-started/"
      },
      {
        text: "Guides",
        link: "/guides/"
      },
      {
        text: "How-To",
        link: "/how-to/"
      },
      {
        text: "Discussions",
        link: "/discussions/"
      },
      {
        text: "Reference",
        link: "/api/"
      },
      {
        text: "Ecosystem",
        items: [
          {
            text: "Help",
            items: [
              {
                text: "FAQ",
                link: "/faq/"
              },
              {
                text: "Chat",
                link: "https://gitter.im/bocadilloproject/bocadillo"
              }
            ]
          },
          {
            text: "Tooling",
            items: [
              {
                text: "Queso (CLI)",
                link: "https://bocadilloproject.github.io/queso"
              }
            ]
          },
          {
            text: "News",
            items: [
              {
                text: "Blog",
                link: "/blog/"
              },
              {
                text: "Mentions",
                link: "/mentions"
              },
              {
                text: "Twitter",
                link: "https://twitter.com/bocadillopy"
              },
              {
                text: "Roadmap",
                link:
                  "https://github.com/bocadilloproject/bocadillo/blob/master/ROADMAP.md"
              }
            ]
          },
          {
            text: "Resources",
            items: [
              {
                text: "Changelog",
                link:
                  "https://github.com/bocadilloproject/bocadillo/blob/master/CHANGELOG.md"
              },
              {
                text: "PyPI",
                link: "https://pypi.org/project/bocadillo/"
              },
              {
                text: "Official repos",
                link: "https://github.com/bocadilloproject"
              }
            ]
          }
        ]
      }
    ],
    sidebar: {
      "/getting-started/": [
        {
          title: "Getting Started",
          collapsable: false,
          children: listDir("getting-started", [
            "",
            "installation",
            "quickstart"
          ])
        }
      ],
      "/guides/": [
        "/guides/app",
        "/guides/cli",
        {
          title: "HTTP",
          collapsable: false,
          children: listDir("guides/http", [
            "routing",
            "views",
            "error-handling",
            "requests",
            "responses",
            "redirecting",
            "media",
            "static-files",
            "hooks",
            "background-tasks",
            "middleware"
          ])
        },
        {
          title: "WebSockets",
          collapsable: false,
          children: listDir("guides/websockets", [
            "",
            "routing",
            "connections",
            "error-handling",
            "messages",
            "example"
          ])
        },
        {
          title: "Protocol-agnostic",
          collapsable: false,
          children: listDir("guides/agnostic", [
            "asgi-middleware",
            "templates",
            "recipes",
            "events"
          ])
        }
      ],
      "/how-to/": [
        {
          title: "How-To",
          collapsable: false,
          children: listDir("how-to", [
            "yaml-media",
            "middleware",
            "tortoise",
            "socketio"
          ])
        }
      ],
      "/discussions/": [
        {
          title: "Discussions",
          collapsable: false,
          children: listDir("discussions", [
            "databases",
            "deployment",
            "security"
          ])
        }
      ],
      "/api/": [
        {
          title: "Python modules",
          collapsable: false,
          children: listDir("api").map(child => {
            const filename = child.split("/")[2];
            const displayName = filename.replace(".md", ".py");
            return [child, displayName];
          })
        }
      ],
      "/faq/": ["/faq/"]
    }
  }
};
