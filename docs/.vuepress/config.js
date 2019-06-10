require("dotenv").config();

const head = require("./head");
const project = require("./project");
const listDir = require("./utils").listDir;

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
    sidebarDepth: 1,
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
        text: "Guide",
        link: "/guide/"
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
            text: "Tooling",
            items: [
              {
                text: "Bocadillo CLI",
                link: project.cli
              }
            ]
          },
          {
            text: "Help",
            items: [
              {
                text: "FAQ",
                link: "/faq"
              },
              {
                text: "Troubleshooting",
                link: "/troubleshooting"
              }
            ]
          },
          {
            text: "News",
            items: [
              {
                text: "Twitter",
                link: `https://twitter.com/${project.twitterUsage}`
              },
              {
                text: "News",
                link: "/news/"
              },
              {
                text: "Mentions",
                link: "/mentions"
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
      "/guide/": [
        "/guide/",
        {
          title: "Getting started",
          children: listDir("guide", ["installation", "async", "tutorial"])
        },
        {
          title: "Essentials",
          children: listDir("guide", [
            "apps",
            "config",
            "routing",
            "requests",
            "responses",
            "errors"
          ])
        },
        {
          title: "Built-in features",
          children: listDir("guide", [
            "json-validation",
            ["builtin-middleware", "CORS, HSTS, GZip"],
            "static-files",
            "sessions",
            "templates",
            "background-tasks"
          ])
        },
        {
          title: "Real-Time Web",
          children: listDir("guide", ["websockets", "sse"])
        },
        {
          title: "Reusability & Modularity",
          children: listDir("guide", [
            "nested-apps",
            "routers",
            "providers",
            "plugins",
            "hooks",
            "middleware",
            "recipes"
          ])
        },
        {
          title: "Tooling",
          children: listDir("guide", ["testing", "cli"])
        }
      ],
      "/how-to/": ["heroku", "orm", "graphql", "socketio", "test-pytest"],
      "/discussions/": ["databases", "frontend", "deployment", "security"],
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
      "/faq": ["/faq"],
      "/troubleshooting": ["/troubleshooting"]
    }
  }
};
