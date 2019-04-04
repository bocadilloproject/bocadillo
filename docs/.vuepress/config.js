const dotenv = require("dotenv");

const head = require("./head");
const project = require("./project");
const listDir = require("./utils").listDir;

dotenv.load();

module.exports = {
  base: "/",
  title: project.title,
  description: project.description,
  lastUpdated: true,
  head,
  serviceWorker: true,
  themeConfig: {
    repo: project.repo,
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
            indexName: project.algoliaIndex
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
                link: `https://gitter.im/${project.repo}`
              }
            ]
          },
          {
            text: "Tooling",
            items: [
              {
                text: "Queso (CLI)",
                link: project.docsPage("queso")
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
                link: `https://twitter.com/${project.twitterUsage}`
              },
              {
                text: "Roadmap",
                link: project.repoPage("ROADMAP.md")
              }
            ]
          },
          {
            text: "Resources",
            items: [
              {
                text: "Changelog",
                link: project.repoPage("CHANGELOG.md")
              },
              {
                text: "PyPI",
                link: `https://pypi.org/project/${project.name}/`
              },
              {
                text: "Official repos",
                link: project.orgLink
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
            "quickstart",
            "tutorial"
          ])
        }
      ],
      "/guides/": [
        "/guides/app",
        {
          title: "Tooling",
          collapsable: false,
          children: listDir("guides/tooling", ["cli", "testing"])
        },
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
            "middleware",
            "sse"
          ])
        },
        {
          title: "WebSockets",
          collapsable: false,
          children: listDir("guides/websockets", [
            "",
            "routing",
            "messages",
            "connections",
            "error-handling",
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
            "events",
            "sessions"
          ])
        },
        {
          title: "Providers (Dependency injection)",
          collapsable: false,
          children: listDir("guides/injection", [
            "",
            "problem",
            "basics",
            "scopes",
            "async",
            "yield",
            "modularity",
            "factory",
            "auto"
          ])
        }
      ],
      "/how-to/": [
        {
          title: "Building upon the framework",
          collapsable: false,
          children: listDir("how-to", ["yaml-media", "middleware", "heroku"])
        },
        {
          title: "Third-party solutions",
          collapsable: false,
          children: listDir("how-to", ["tortoise", "socketio"])
        },
        {
          title: "Testing",
          collapsable: false,
          children: listDir("how-to", ["test-pytest"])
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
