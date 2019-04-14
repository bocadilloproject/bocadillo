export default ({ Vue, router }) => {
  router.addRoutes([
    // After renaming "Topics" section to "Guides"
    { path: "/topics/", redirect: "/guides/" },
    { path: "/guides/app.html", redirect: "/guides/architecture/app.html" },
    {
      path: "/guides/agnostic/recipes.html",
      redirect: "/guides/architecture/recipes.html"
    },
    {
      path: "/guides/agnostic/events.html",
      redirect: "/guides/architecture/events.html"
    },
    {
      path: "/guides/tooling/testing.html",
      redirect: "/guides/architecture/testing.html"
    }
  ]);
};
