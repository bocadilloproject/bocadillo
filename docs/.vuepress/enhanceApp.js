const toGuides = [
  "/guides/",
  ...["architecture", "http", "websockets", "agnostic"].map(
    section => `/guides/${section}/:path?`
  ),
  "/topics/",
  "/getting-started/"
];

// See #279
const docsOverhaulRoutes = [
  {
    path: "/guides/injection/*",
    redirect: "/guide/providers.html"
  },
  {
    path: "/guides/async.html",
    redirect: "/guide/async.html"
  },
  ...toGuides.map(source => ({
    path: `${source}`,
    redirect: "/guide/:path"
  }))
];

export default ({ Vue, router }) => {
  Vue.prototype.$version = "0.16.1";
  router.addRoutes([
    ...docsOverhaulRoutes,
    {
      path: "/blog/",
      redirect: "/news/"
    },
    {
      path: "/blog/:path",
      redirect: "/news/:path"
    }
  ]);
};
