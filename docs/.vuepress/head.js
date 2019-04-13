const project = require("./project");

// Change the version to force web browsers to refresh favicons.
const faviconVersion = "lk90Ny5lbz";

function versioned(value) {
  return faviconVersion ? `${value}?v=${faviconVersion}` : value;
}

module.exports = [
  // Favicon hints.
  [
    "link",
    {
      rel: "shortcut icon",
      href: versioned("/favicon.ico")
    }
  ],
  [
    "link",
    {
      rel: "icon",
      type: "image/png",
      sizes: "32x32",
      href: versioned("/favicon-32x32.png")
    }
  ],
  [
    "link",
    {
      rel: "icon",
      type: "image/png",
      sizes: "16x16",
      href: versioned("/favicon-16x16.png")
    }
  ],

  // Android.
  ["link", { rel: "manifest", href: versioned("/site.webmanifest") }],
  ["meta", { name: "theme-color", content: "#ffe66b" }],

  // Apple.
  [
    "link",
    {
      rel: "apple-touch-icon",
      sizes: "180x180",
      href: versioned("/apple-touch-icon.png")
    }
  ],
  [
    "link",
    {
      rel: "mask-icon",
      href: versioned("/safari-pinned-tab.svg"),
      color: "#91ba3f"
    }
  ],

  // Windows.
  ["meta", { name: "msapplication-TileColor", content: "#ef9a4d" }],

  // Twitter cards.
  ["meta", { name: "twitter:card", content: "summary" }],
  ["meta", { name: "twitter:url", content: project.docs }],
  ["meta", { name: "twitter:title", content: project.title }],
  ["meta", { name: "twitter:site", content: project.title }],
  ["meta", { name: "twitter:creator", content: project.author }],
  ["meta", { name: "twitter:description", content: project.description }],
  [
    "meta",
    {
      name: "twitter:image",
      content: "https://bocadilloproject.github.io/social-image.png"
    }
  ],

  // Google Search Console.
  [
    "meta",
    {
      name: "google-site-verification",
      content: "xbJzBKn7IuLWAUKvqHo1c3vMelw3eTRL0k3JcKjYB_k"
    }
  ]
];
